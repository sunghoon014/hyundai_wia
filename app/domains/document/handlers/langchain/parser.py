import re
import unicodedata

import pandas as pd
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def _preprocess_text(text: str) -> str:
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


async def parse_with_langchain(
    path: str, ext: str = "txt", file_name: str = "text"
) -> list[Document]:
    if ext == "txt":
        # 파일 읽기
        try:
            with open(path, encoding="utf-8") as file:
                text = file.read()
            data = _preprocess_text(text)
        except Exception as e:
            raise RuntimeError(f"Error loading {path}") from e

        # 텍스트 분할
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
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
        chunks = text_splitter.split_text(data)
        chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
        all_documents = []
        for chunk in chunks:
            all_documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "type": "text",
                        "title": file_name,
                        "url": path,
                        "page_number": "",
                        "summary": "",
                    },
                )
            )
        return all_documents
    elif ext == "csv":
        try:
            # 행이 너무 크면 메모리 에러가 발생하여 50개의 로우로 청킹
            chunk_csv = pd.read_csv(path, chunksize=50)
        except Exception as e:
            raise RuntimeError(f"Error loading {path}") from e

        all_documents = []
        for chunk_c in chunk_csv:
            if chunk_c.dropna().empty:
                continue

            markdown_table = chunk_c.dropna().to_markdown(index=False)
            if markdown_table == "":
                continue

            # 테이블 저장
            all_documents.append(
                Document(
                    page_content=markdown_table,
                    metadata={
                        "type": "table",
                        "title": file_name,
                        "url": path,
                        "page_number": "",
                        "summary": "",
                    },
                )
            )
        return all_documents
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
