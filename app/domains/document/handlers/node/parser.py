import asyncio
import json
import os
import time
from collections.abc import AsyncGenerator

import requests

from app.common.logger import logger
from app.domains.document.handlers.node.base import BaseNode
from app.domains.document.schemas.state import ParseState


class UpstageParseNode(BaseNode):
    def __init__(self, api_key, is_save=False):
        """Upstage Layout OCR.

        :param api_key: Upstage API 인증을 위한 API 키

        config 참고: https://docs.upstage.ai/reference/document-digitization
        """
        self.name = "upstage_parse_node"
        self.api_key = api_key
        self.is_save = is_save
        self.config = {
            "model": "document-parse",
            "chart_recognition": True,
            "ocr": "force",
            "output_formats": "['text', 'markdown']",
            "coordinates": True,
            "base64_encoding": "['figure', 'chart', 'table']",
        }

    def _upstage_ocr_sync(self, input_filepath: str) -> dict:
        """Upstage의 OCR API를 호출하여 이미지 분석을 수행합니다.

        :param input_filepath: 분석할 PDF 파일 경로
        :return: 분석 결과 (JSON 딕셔너리)
        """
        # API 요청 헤더 설정
        headers = {"Authorization": f"Bearer {self.api_key}"}

        # 분석할 PDF 파일
        with open(input_filepath, "rb") as doc_file:
            files = {"document": doc_file}

            # API 요청 보내기
            response = requests.post(
                "https://api.upstage.ai/v1/document-digitization",
                headers=headers,
                data=self.config,
                files=files,
            )

        # API 응답 처리 및 결과 저장
        if response.status_code == 200:
            # 분석 결과를 저장할 JSON 파일 경로 생성
            output_file = os.path.splitext(input_filepath)[0] + ".json"
            parsed_json = response.json()
            if self.is_save:
                # 분석 결과를 저장할 JSON 파일 경로 생성
                try:
                    with open(output_file, "w") as f:
                        # ensure_ascii=False로 설정하여 한글이 제대로 저장되도록 함
                        json.dump(parsed_json, f, ensure_ascii=False, indent=4)
                    logger.info(f"Upstage OCR API 요청 성공. 결과 저장: {output_file}")
                except Exception as e:
                    logger.error(f"Upstage OCR API 요청 성공. 결과 저장 실패: {e}")
            return parsed_json
        else:
            logger.error(f"Upstage OCR API 요청 실패. 상태 코드: {response.text}")
            raise ValueError(f"Upstage OCR API 요청 실패. 상태 코드: {response.text}")

    def parse_start_end_page(self, filepath):
        # 파일명에서 페이지 번호 추출 (예: WorldEnergyOutlook2024_0040_0049.pdf)
        filename = os.path.basename(filepath)
        # .pdf 확장자 제거
        name_without_ext = filename.rsplit(".", 1)[0]

        # 파일명 형식 검증
        try:
            # 파일명이 최소 9자 이상이어야 함
            if len(name_without_ext) < 9:
                return (-1, -1)

            # 마지막 9자리 추출 (예: 0040_0049)
            page_numbers = name_without_ext[-9:]

            # 형식이 ####_#### 인지 검증 (숫자4개_숫자4개)
            if not (
                page_numbers[4] == "_"
                and page_numbers[:4].isdigit()
                and page_numbers[5:].isdigit()
            ):
                return (-1, -1)

            # 시작 페이지와 끝 페이지 추출
            start_page = int(page_numbers[:4])
            end_page = int(page_numbers[5:])

            # 시작 페이지가 끝 페이지보다 크면 검증 실패
            if start_page > end_page:
                return (-1, -1)

            return (start_page, end_page)

        except (IndexError, ValueError):
            return (-1, -1)

    async def execute(self, state: ParseState) -> AsyncGenerator[ParseState, None]:
        """주어진 입력 파일에 대해 문서 분석을 비동기적으로 실행합니다.

        :param state: ParseState 객체
        :return: 분석 결과 딕셔너리
        """
        start_time = time.time()
        filepath = state["working_filepath"]
        logger.info(f"Start Parsing: {filepath}")

        # 동기 함수를 별도 스레드에서 실행
        parsed_json = await asyncio.to_thread(self._upstage_ocr_sync, filepath)

        start_page, _ = self.parse_start_end_page(filepath)
        page_offset = start_page - 1 if start_page != -1 else 0

        # 페이지 번호 재계산
        for element in parsed_json["elements"]:
            element["page"] += page_offset + 1

        # 메타데이터 추출
        metadata = {
            "api": parsed_json.pop("api"),
            "model": parsed_json.pop("model"),
            "usage": parsed_json.pop("usage"),
        }

        duration = time.time() - start_time
        logger.info(f"Finished Parsing in {duration:.2f} seconds")

        # 상태 업데이트 또는 결과 반환
        yield {
            "parse_elements": [parsed_json["elements"]],
            "parse_metadata": [metadata],
        }


class PostParseNode(BaseNode):
    def __init__(self):
        self.name = "post_parse_node"

    def execute(self, state: ParseState):
        elements_list = state["parse_elements"]
        id_counter = 0  # ID를 순차적으로 부여하기 위한 카운터
        post_processed_elements = []

        for elements in elements_list:
            for element in elements:
                elem = element.copy()
                # ID 순차적으로 부여
                elem["id"] = id_counter
                id_counter += 1

                post_processed_elements.append(elem)

        logger.info(f"Total Post-processed Elements: {id_counter}")

        pages_count = 0
        metadata = state["parse_metadata"]

        for meta in metadata:
            for k, v in meta.items():
                if k == "usage":
                    pages_count += int(v["pages"])

        # TODO: OCR 플랫폼 별 비용 계산할 수 있도록 변경
        total_cost = pages_count * 0.01

        logger.info(f"Total Cost: ${total_cost:.2f} / {pages_count} pages")

        # 재정렬된 elements를 state에 업데이트
        return {
            "post_parse_elements": post_processed_elements,
            "parse_cost": total_cost,
        }
