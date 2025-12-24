import os

import httpx

from app.domains.document.handlers.node.base import BaseNode
from app.domains.document.schemas.state import ParseState


class WorkingQueueNode(BaseNode):
    def execute(self, state: ParseState):
        working_filepath = state.get("working_filepath", None)
        # working_filepath가 없거나 비어있는 경우 첫번째 파일 선택
        if (
            "working_filepath" not in state
            or state["working_filepath"] is None
            or state["working_filepath"] == ""
        ):
            if len(state["split_filepaths"]) > 0:
                working_filepath = state["split_filepaths"][0]
            else:
                working_filepath = "<<FINISHED>>"
        else:
            if working_filepath == "<<FINISHED>>":
                return {"working_filepath": "<<FINISHED>>"}

            # 현재 작업중인 파일의 인덱스 찾기
            current_index = state["split_filepaths"].index(working_filepath)
            # 다음 파일이 있으면 다음 파일을 선택, 없으면 FINISHED 표시
            if current_index + 1 < len(state["split_filepaths"]):
                working_filepath = state["split_filepaths"][current_index + 1]
            else:
                working_filepath = "<<FINISHED>>"
        return {"working_filepath": working_filepath}


def continue_parse(state: ParseState):
    return state["working_filepath"] != "<<FINISHED>>"


async def download_file_to_firebase_url(document_url: str, save_path: str):
    """지정된 URL에서 파일을 다운로드하여 제공된 경로에 저장합니다.

    Args:
        document_url (str): 다운로드할 파일의 URL입니다.
        save_path (str): 파일을 저장할 전체 경로 (파일명 포함)입니다.

    Returns:
        str: 파일이 저장된 경로. 오류 발생 시 None을 반환합니다.
    """
    try:
        # 저장 경로의 디렉토리가 존재하는지 확인하고, 없으면 생성합니다.
        save_dir = os.path.dirname(save_path)
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)

        async with (
            httpx.AsyncClient() as client,
            client.stream("GET", document_url) as response,
        ):
            response.raise_for_status()
            with open(save_path, "wb") as f:
                async for chunk in response.aiter_bytes():
                    f.write(chunk)
        return save_path
    except Exception as e:
        print(f"파일 다운로드 중 오류 발생: {e}")
        return None
