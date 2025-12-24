import re
import unicodedata

from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.common.logger import logger
from app.domains.document.handlers.node.base import BaseNode
from app.domains.document.schemas.state import ParseState


class LangchainDocumentNode(BaseNode):
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
        strategy: str = "recursive",  # semantic, recursive
        embedding_model: str = "text-embedding-3-small",
    ):
        self.name = "langchain_document_node"
        if strategy == "semantic":
            self.text_splitter = SemanticChunker(
                embeddings=OpenAIEmbeddings(model=embedding_model),
                buffer_size=2,  # 2문장씩 그룹화 (적당한 컨텍스트)
                breakpoint_threshold_type="percentile",  # 가장 안정적
                breakpoint_threshold_amount=0.85,  # 조금 더 많이 분할하도록 조정
                add_start_index=True,  # 위치 정보 유용
                sentence_split_regex=r"(?<=[.!?])\s+",  # 영어 문장 분할 개선
            )
        elif strategy == "recursive":
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                keep_separator=False,
                separators=[
                    # 큰 구조부터 분할 (overlap이 제대로 작동하도록)
                    "\n\n\n",  # 큰 섹션 구분 (최우선)
                    "\n\n",  # 문단 구분 (두 번째 우선)
                    "\nChapter ",  # 챕터
                    "\nSection ",  # 섹션
                    "\nFigure ",  # 그림
                    "\nTable ",  # 테이블
                    "\n• ",  # 불릿 포인트
                    "\n- ",  # 대시 리스트
                    "\n1. ",  # 숫자 리스트
                    "\n",  # 일반 줄바꿈
                    # 문장 구분자는 나중에 (overlap 보장을 위해)
                    ". ",  # 문장 끝
                    "! ",  # 감탄문
                    "? ",  # 의문문
                    ".\n",  # 줄바꿈이 있는 문장
                    "!\n",
                    "?\n",
                    "; ",  # 세미콜론
                    ", ",  # 콤마 (마지막 수단)
                    " ",  # 공백 (최후 수단)
                    "",  # 문자 (진짜 마지막)
                ],
                length_function=len,
                is_separator_regex=False,
            )

    def _extract_tag_content(self, content: str, tag: str) -> str | None:
        pattern = rf"<{tag}>(.*?)</{tag}>"
        match = re.search(pattern, content, re.DOTALL)

        if match:
            return match.group(1).strip()
        else:
            return None

    def _extract_non_tag_content(self, content: str, tag: str) -> str:
        pattern = rf"<{tag}>.*?</{tag}>"
        result = re.sub(pattern, "", content, flags=re.DOTALL)
        return result.strip()

    def _create_document(self, content, metadata):
        """문서 객체를 생성합니다.

        Args:
            content (str): 문서의 내용
            metadata (dict): 문서의 메타데이터

        Returns:
            Document: 생성된 문서 객체
        """
        return Document(page_content=content, metadata=metadata)

    def _preprocess_text(self, text: str) -> str:
        """텍스트 전처리."""
        # 1. 유니코드 정규화 - 같은 문자를 통일된 방식으로 표현
        # 예: "café" (e + ´) → "café" (é)
        text = unicodedata.normalize("NFKC", text)

        # 2. 연속된 공백 통일
        # 예: "word    multiple    spaces" → "word multiple spaces"
        text = re.sub(r" {2,}", " ", text)

        # 3. 연속된 줄바꿈 정리 (보고서에서 자주 발생)
        # 예: "paragraph\n\n\n\n\nnext" → "paragraph\n\nnext"
        text = re.sub(r"\n{3,}", "\n\n", text)

        # 4. 탭을 공백으로 변환
        # 예: "word\t\ttab\tspaces" → "word  tab spaces"
        text = text.replace("\t", " ")

        # 5. 단일 줄바꿈을 공백으로 변환 (문단 구분은 유지)
        # 예: "spring\nturnaround season" → "spring turnaround season"
        # 단, 문단 구분(\n\n)은 유지
        text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)

        # 6. 문장 끝 공백 정리 (보고서에서 중요!)
        # 예: "sentence.   Next sentence" → "sentence. Next sentence"
        text = re.sub(r"([.!?])\s+", r"\1 ", text)

        # 7. 보고서에서 자주 나오는 특수 공백 문자 제거
        # Non-breaking space, em space, thin space 등
        text = re.sub(r"[\u00A0\u2000-\u200B\u2028\u2029]", " ", text)
        # Zero-width 문자들 (복사-붙여넣기 시 자주 생김)
        text = re.sub(r"[\u200C\u200D\uFEFF]", "", text)

        # 8. 각 줄의 시작/끝 공백 제거 (남은 줄바꿈들에 대해)
        lines = text.split("\n")
        lines = [line.strip() for line in lines]
        text = "\n".join(lines)

        # 9. 위 과정에서 생긴 추가 공백들 재정리
        text = re.sub(r" {2,}", " ", text)

        # 10. 전체 텍스트 양끝 공백 제거
        text = text.strip()

        return text

    def _split_text_with_strategy(self, text: str) -> list[str]:
        """텍스트를 전략에 따라 분할합니다 (문장 완성도 보장!)."""
        # 전처리 적용
        processed_text = self._preprocess_text(text)

        # 텍스트가 너무 짧으면 그냥 반환
        if len(processed_text.strip()) < 50:
            return [processed_text] if processed_text.strip() else []

        try:
            # 기본 청킹
            chunks = self.text_splitter.split_text(processed_text)

            # 빈 청크 제거 및 후처리
            chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
            return chunks

        except Exception as e:
            logger.warning(
                f"Text splitting failed with {self.strategy} strategy: {str(e)}"
            )
            # 안전한 fallback: 문장 단위 분할
            return self._split_by_sentences(processed_text)

    async def execute(self, state: ParseState):
        logger.info("Start creating documents...")
        filepath = state.get("filepath", None)
        file_name = state.get("file_name", None)
        page_summary = state.get("page_summary", None)
        image_summary = state.get("image_summary", None)
        table_summary = state.get("table_summary", None)

        all_documents = []
        for p in page_summary:
            page_text = p.get("page_raw")
            splitted_text = self._split_text_with_strategy(page_text)
            for text in splitted_text:
                all_documents.append(
                    self._create_document(
                        text,
                        metadata={
                            "type": "paragraph",
                            "title": file_name,
                            "url": filepath,
                            "page_number": p.get("page"),
                            "summary": p.get("page_summary"),
                        },
                    )
                )

        for i in image_summary:
            text = i.get("image_summary")
            # 이미지 요약 부분만 따로 저장
            summary_text = self._extract_non_tag_content(text, "hypothetical_questions")
            # 질문만 따로 저장
            hypothetical_questions = self._extract_tag_content(
                text, "hypothetical_questions"
            )
            if summary_text and hypothetical_questions:
                all_documents.append(
                    self._create_document(
                        summary_text,
                        metadata={
                            "type": "image",
                            "title": file_name,
                            "url": filepath,
                            "page_number": i.get("page"),
                            "summary": i.get("image_raw"),
                        },
                    )
                )
                all_documents.append(
                    self._create_document(
                        hypothetical_questions,
                        metadata={
                            "type": "image",
                            "title": file_name,
                            "url": filepath,
                            "page_number": i.get("page"),
                            "summary": i.get("image_raw"),
                        },
                    )
                )
            else:
                all_documents.append(
                    self._create_document(
                        text,
                        metadata={
                            "type": "image",
                            "title": file_name,
                            "url": filepath,
                            "page_number": i.get("page"),
                            "summary": i.get("image_raw"),
                        },
                    )
                )

        for t in table_summary:
            text = t.get("table_summary")
            # 테이블 요약 부분만 따로 저장
            summary_text = self._extract_non_tag_content(text, "hypothetical_questions")
            # 질문만 따로 저장
            hypothetical_questions = self._extract_tag_content(
                text, "hypothetical_questions"
            )
            if summary_text and hypothetical_questions:
                all_documents.append(
                    self._create_document(
                        summary_text,
                        metadata={
                            "type": "table",
                            "title": file_name,
                            "url": filepath,
                            "page_number": t.get("page"),
                            "summary": t.get("table_raw"),
                        },
                    )
                )
                all_documents.append(
                    self._create_document(
                        hypothetical_questions,
                        metadata={
                            "type": "table",
                            "title": file_name,
                            "url": filepath,
                            "page_number": t.get("page"),
                            "summary": t.get("table_raw"),
                        },
                    )
                )
            else:
                all_documents.append(
                    self._create_document(
                        text,
                        metadata={
                            "type": "table",
                            "title": file_name,
                            "url": filepath,
                            "page_number": t.get("page"),
                            "summary": t.get("table_raw"),
                        },
                    )
                )
        logger.info(f"Created {len(all_documents)} langchain documents")
        yield {"documents": all_documents}
