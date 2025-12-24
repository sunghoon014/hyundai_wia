import operator
from typing import Annotated, TypedDict


class ParseState(TypedDict):
    # 파일 입력
    ext: Annotated[str, "ext"]  # 파일 확장자
    file_name: Annotated[str, "file_name"]  # 원본 파일 이름
    filepath: Annotated[str, "filepath"]  # 원본 파일경로
    save_dir: Annotated[str, "save_dir"]  # 분할된 파일 저장 디렉토리
    split_filepaths: Annotated[list[str], "split_filepaths"]  # 분할된 파일 경로
    working_filepath: Annotated[str, "working_filepath"]  # 현재 작업중인 파일

    # ParseNode 결과
    parse_elements: Annotated[list[str], operator.add]  # Parse 결과
    parse_metadata: Annotated[list[str], operator.add]  # Parse 메타데이터
    post_parse_elements: Annotated[list[str], "post_parse_elements"]  # Post Parse 결과
    parse_cost: Annotated[float, "parse_cost"]  # Parse 비용

    # LLM 결과
    page_summary: Annotated[dict[str, str], "page_summary"]
    document_summary: Annotated[dict[str, str], "document_summary"]
    image_summary: Annotated[list[dict[str, str]], "image_summary"]
    table_summary: Annotated[list[dict[str, str]], "table_summary"]

    # RAG를 위한 Document 생성
    documents: Annotated[list[dict[str, str]], "documents"]
