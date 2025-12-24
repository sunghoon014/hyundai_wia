import asyncio
import re
from functools import partial
from typing import Any

# 효과적인 전처리를 위한 imports
import nltk
from langchain_core.documents import Document as LangchainDocument
from langchain_openai import OpenAIEmbeddings
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    Function,
    FunctionType,
    connections,
    utility,
)

from app.common.logger import logger

# NLTK 데이터 다운로드 (처음 실행시에만)
try:
    nltk.data.find("tokenizers/punkt")
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("punkt", quiet=True)
    nltk.download("stopwords", quiet=True)


class MilvusIndexer:
    """pymilvus를 사용하여 하이브리드 검색(Dense + Sparse)을 위한 인덱스를 구축하고 관리합니다.

    이 클래스는 컬렉션을 완전히 다시 만드는 "drop and recreate" 전략을 사용하여 항상 모든 문서에 대한 최신 인덱스를 유지합니다.
    Milvus 2.5/2.6의 내장 BM25 Function을 사용하여 자동으로 sparse embedding을 생성합니다.
    원본 텍스트는 dense embedding용, 전처리된 텍스트는 sparse embedding용으로 분리 저장합니다.
    """

    def __init__(
        self,
        connection_alias: str,
        dense_vector_dim: int,
        embedding_model: str = "text-embedding-3-small",
        enable_nltk: bool = False,
    ):
        """MilvusIndexer를 초기화합니다.

        Args:
            embedding_model (str): Dense 임베딩을 생성할 OpenAI 모델의 이름입니다.
            connection_alias (str): 사용할 Milvus 연결 별칭입니다.
            dense_vector_dim (int): Dense 임베딩의 차원입니다.
            enable_nltk (bool): NLTK 사용 여부입니다.
        """
        self.connection_alias = connection_alias
        logger.info(
            f"connection_alias: {self.connection_alias} dense_vector_dim: {dense_vector_dim}, embedding_model: {embedding_model}, enable_nltk: {enable_nltk}"
        )
        self.enable_nltk = enable_nltk

        # 연결 설정
        connections.connect(self.connection_alias, address="127.0.0.1:19530")

        # 필드 이름 정의
        self.pk_field = "doc_id"
        self.text_original_field = "text_original"  # Dense embedding용 원본 텍스트
        self.text_processed_field = "text_processed"  # BM25용 전처리된 텍스트
        self.dense_vector_field = "dense_vector"
        self.sparse_vector_field = "sparse_vector"

        # Dense 임베딩 모델만 초기화 (sparse는 내장 BM25 Function 사용)
        self.dense_embedder = OpenAIEmbeddings(model=embedding_model)
        self.dense_vector_dim = dense_vector_dim

        # 전처리 도구 초기화
        if self.enable_nltk:
            self.stemmer = PorterStemmer()
            self.stop_words = set(stopwords.words("english"))
        else:
            self.stemmer = None
            self.stop_words = set()

    def _preprocess_text_for_bm25(self, text: str) -> str:
        """BM25 검색 성능 향상을 위한 텍스트 전처리를 수행합니다.

        전처리 단계:
        1. 소문자 변환
        2. 특수문자 및 숫자 제거 (선택적 보존)
        3. 토큰화
        4. 불용어 제거 (옵션)
        5. 어간 추출 (Stemming)

        Args:
            text (str): 전처리할 원본 텍스트

        Returns:
            str: 전처리된 텍스트
        """
        if not text or not text.strip():
            return ""

        # 1. 소문자 변환
        text = text.lower()

        # 2. 기본 정리: 연속된 공백, 탭, 개행문자 정규화
        text = re.sub(r"\s+", " ", text).strip()

        if not self.enable_nltk:
            return text

        try:
            # 3. 토큰화
            tokens = word_tokenize(text)

            # 4. 필터링 및 전처리
            processed_tokens = []
            for token in tokens:
                # 최소 길이 체크 (1글자 단어 제외, 단 'i', 'a' 같은 중요한 단어는 보존)
                if len(token) < 2 and token.lower() not in {"i", "a"}:
                    continue

                # 숫자만으로 구성된 토큰 제외
                if token.isdigit():
                    continue

                # 특수문자만으로 구성된 토큰 제외
                if not re.search(r"[a-zA-Z]", token):
                    continue

                # 불용어 제거
                if self.enable_nltk and token.lower() in self.stop_words:
                    continue

                # 어간 추출
                stemmed_token = self.stemmer.stem(token)
                processed_tokens.append(stemmed_token)

            # 5. 결과 반환
            processed_text = " ".join(processed_tokens)
            return processed_text if processed_text else text.lower()  # fallback

        except Exception as e:
            logger.warning(
                f"텍스트 전처리 중 오류 발생: {e}. 기본 전처리를 사용합니다."
            )
            # fallback: 기본 전처리
            text = re.sub(r"[^\w\s]", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
            return text

    def _create_collection(self, collection_name: str):
        """하이브리드 검색을 위한 새로운 컬렉션을 생성합니다. 기존 컬렉션이 있다면 삭제합니다."""
        if utility.has_collection(collection_name, using=self.connection_alias):
            logger.info(f"기존 컬렉션을 삭제합니다: {collection_name}")
            utility.drop_collection(collection_name, using=self.connection_alias)

        logger.info(f"새로운 컬렉션을 생성합니다: {collection_name}")
        # TODO: 컬렉션 생성 시 파라미터 config에서 관리하도록 변경 필요
        try:
            pk_field = FieldSchema(
                name=self.pk_field,
                dtype=DataType.VARCHAR,
                is_primary=True,
                max_length=64,
                auto_id=False,
            )

            # 원본 텍스트 필드 (Dense embedding용)
            text_original_field = FieldSchema(
                name=self.text_original_field,
                dtype=DataType.VARCHAR,
                max_length=65535,
                description="원본 텍스트 (Dense embedding 생성용)",
            )

            # 전처리된 텍스트 필드 (BM25 Function용)
            text_processed_field = FieldSchema(
                name=self.text_processed_field,
                dtype=DataType.VARCHAR,
                max_length=65535,
                enable_analyzer=True,  # BM25 Function을 위해 analyzer 활성화
                description="전처리된 텍스트 (BM25 Sparse embedding 생성용)",
            )

            dense_field = FieldSchema(
                name=self.dense_vector_field,
                dtype=DataType.FLOAT_VECTOR,
                dim=self.dense_vector_dim,
            )
            sparse_field = FieldSchema(
                name=self.sparse_vector_field,
                dtype=DataType.SPARSE_FLOAT_VECTOR,
                description="BM25 Function으로 자동 생성되는 sparse embedding",
            )

            schema = CollectionSchema(
                fields=[
                    pk_field,
                    text_original_field,
                    text_processed_field,
                    dense_field,
                    sparse_field,
                ],
                enable_dynamic_field=True,
            )

            # BM25 Function 추가 - 전처리된 텍스트를 input으로 사용
            bm25_function = Function(
                name="text_bm25_emb",
                input_field_names=[self.text_processed_field],  # 전처리된 텍스트 사용
                output_field_names=[self.sparse_vector_field],
                function_type=FunctionType.BM25,
            )
            schema.add_function(bm25_function)

            collection = Collection(
                name=collection_name, schema=schema, using=self.connection_alias
            )

            # Dense vector 인덱스 생성 (OpenAI embedding에 최적화: 정규화된 벡터이므로 IP 사용)
            dense_index = {"index_type": "AUTOINDEX", "metric_type": "IP", "params": {}}
            collection.create_index(
                field_name=self.dense_vector_field, index_params=dense_index
            )

            # Sparse vector 인덱스 생성 (BM25 Function 사용시 metric_type은 BM25)
            sparse_index = {
                "index_type": "SPARSE_INVERTED_INDEX",
                "metric_type": "BM25",  # BM25 Function 사용시 BM25 metric 필수
                "params": {},
            }
            collection.create_index(
                field_name=self.sparse_vector_field, index_params=sparse_index
            )

            logger.info(f"컬렉션 '{collection_name}'이(가) 성공적으로 생성되었습니다.")
            logger.info(
                f"전처리 설정: NLTK={'사용 중' if self.enable_nltk else '사용 불가'}"
            )
            return collection
        except Exception as e:
            logger.error(f"컬렉션 '{collection_name}' 생성에 실패했습니다: {e}")
            raise

    async def aindex_documents(self, documents: list[dict[str, Any]]):
        """문서 리스트를 받아 Milvus에 하이브리드 검색을 위해 인덱싱합니다.

        이 메서드는 기존 컬렉션을 삭제하고 모든 문서를 새로 인덱싱합니다.
        원본 텍스트는 dense embedding용으로, 전처리된 텍스트는 BM25 Function의 sparse embedding용으로 사용됩니다.
        """
        collection_name = documents[0]["collection_name"]
        logger.info(f"collection_name: {collection_name}")

        try:
            langchain_docs = []
            for doc in documents:
                if isinstance(doc["content"], list):
                    for content_doc in doc["content"]:
                        page_content = content_doc["page_content"]
                        metadata = content_doc["metadata"]
                        langchain_docs.append(
                            LangchainDocument(
                                page_content=page_content,
                                metadata=metadata,
                            )
                        )
        except Exception as e:
            logger.error(f"문서 인덱싱 중 오류가 발생했습니다: {e}")
            raise e

        if not langchain_docs:
            logger.warning("인덱싱할 내용이 있는 문서가 없습니다.")
            return

        # 1. 컬렉션 재생성
        loop = asyncio.get_running_loop()
        collection = await loop.run_in_executor(
            None, self._create_collection, collection_name
        )

        # 2. 원본 텍스트와 전처리된 텍스트 준비
        original_corpus = [doc.page_content for doc in langchain_docs]
        processed_corpus = [
            self._preprocess_text_for_bm25(doc.page_content) for doc in langchain_docs
        ]

        logger.info("전처리 예시:")
        if original_corpus:
            logger.info(f"원본: {original_corpus[0][:100]}...")
            logger.info(f"전처리: {processed_corpus[0][:100]}...")

        # 3. Dense 임베딩 생성 (원본 텍스트 기반)
        dense_embeddings = await self.dense_embedder.aembed_documents(original_corpus)

        # 4. 삽입할 데이터 준비
        data_to_insert = []
        failed_documents = []

        for i, doc in enumerate(langchain_docs):
            try:
                doc_id = str(i)
                data = doc.metadata.copy()
                data[self.pk_field] = doc_id
                data[self.text_original_field] = doc.page_content  # 원본 텍스트
                data[self.text_processed_field] = processed_corpus[i]  # 전처리된 텍스트
                data[self.dense_vector_field] = dense_embeddings[
                    i
                ]  # 원본 기반 dense embedding
                # sparse_vector_field는 BM25 Function이 text_processed_field로부터 자동 생성
                data_to_insert.append(data)
            except Exception as e:
                logger.warning(f"문서 {i} 데이터 준비 중 오류 발생 (건너뜀): {e}")
                failed_documents.append({"index": i, "error": str(e)})
                continue

        if not data_to_insert:
            logger.error("삽입할 유효한 문서 데이터가 없습니다.")
            return

        # 5. 배치 단위로 데이터 삽입 (에러 발생시 개별 문서로 진행)
        # TODO: 컬렉션 생성 시 파라미터 config에서 관리하도록 변경 필요
        batch_size = 100  # 배치 크기
        total_inserted = 0
        total_failed = len(failed_documents)

        def _insert_batch_sync(batch_data):
            try:
                collection.insert(batch_data)
                return len(batch_data), []
            except Exception as e:
                logger.warning(f"배치 삽입 실패 ({len(batch_data)}개 문서): {e}")
                # 배치 실패시 개별 문서로 재시도
                successful_count = 0
                failed_items = []

                for item in batch_data:
                    try:
                        collection.insert([item])
                        successful_count += 1
                    except Exception as individual_error:
                        failed_items.append(
                            {
                                "doc_id": item.get(self.pk_field, "unknown"),
                                "error": str(individual_error),
                            }
                        )
                        logger.warning(
                            f"문서 {item.get(self.pk_field, 'unknown')} 삽입 실패 (건너뜀): {individual_error}"
                        )

                return successful_count, failed_items

        # 배치별로 처리
        for i in range(0, len(data_to_insert), batch_size):
            batch = data_to_insert[i : i + batch_size]
            batch_inserted, batch_failed = await loop.run_in_executor(
                None, _insert_batch_sync, batch
            )
            total_inserted += batch_inserted
            total_failed += len(batch_failed)

            logger.info(f"배치 {i//batch_size + 1} 처리 완료: {batch_inserted}개 성공")

        # 최종 flush
        def _final_flush():
            try:
                collection.flush()
                logger.info("데이터 flush 완료")
            except Exception as e:
                logger.error(f"데이터 flush 중 오류 발생: {e}")
                raise

        await loop.run_in_executor(None, _final_flush)

        # 최종 결과 로깅
        total_processed = len(langchain_docs)
        logger.info("문서 인덱싱 완료:")
        logger.info(f"  - 총 문서 수: {total_processed}개")
        logger.info(f"  - 성공: {total_inserted}개")
        logger.info(f"  - 실패: {total_failed}개")
        logger.info(f"  - 성공률: {(total_inserted/total_processed)*100:.1f}%")
        logger.info("하이브리드 검색 준비 완료: Dense(원본) + Sparse(전처리)")

    async def alist_collections(self) -> list[str]:
        """Milvus에 있는 모든 컬렉션의 이름을 반환합니다."""
        try:
            loop = asyncio.get_running_loop()
            func = partial(utility.list_collections, using=self.connection_alias)
            collections = await loop.run_in_executor(None, func)
            logger.info(f"사용 가능한 컬렉션: {collections}")
            return collections
        except Exception as e:
            logger.error(f"컬렉션 목록 조회에 실패했습니다: {e}")
            raise

    async def adelete_collection(self, collection_name: str):
        """지정된 이름의 컬렉션을 삭제합니다."""

        def _delete_sync():
            if utility.has_collection(collection_name, using=self.connection_alias):
                utility.drop_collection(collection_name, using=self.connection_alias)
                logger.info(
                    f"컬렉션 '{collection_name}'이(가) 성공적으로 삭제되었습니다."
                )
            else:
                logger.warning(
                    f"삭제할 컬렉션 '{collection_name}'을(를) 찾을 수 없습니다."
                )

        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, _delete_sync)
        except Exception as e:
            logger.error(f"컬렉션 '{collection_name}' 삭제에 실패했습니다: {e}")
            raise

    async def aclear_all_collections(self):
        """Milvus의 모든 컬렉션을 삭제합니다."""

        def _clear_sync():
            collections = utility.list_collections(using=self.connection_alias)
            if not collections:
                logger.info("삭제할 컬렉션이 없습니다.")
                return

            for collection_name in collections:
                utility.drop_collection(collection_name, using=self.connection_alias)
            logger.info(
                f"모든 컬렉션({len(collections)}개)이 성공적으로 삭제되었습니다."
            )

        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, _clear_sync)
        except Exception as e:
            logger.error(f"모든 컬렉션 삭제에 실패했습니다: {e}")
            raise
