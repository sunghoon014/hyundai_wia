import asyncio
import os
from collections.abc import AsyncGenerator
from urllib.parse import urlparse

import aiohttp
import pymupdf

from app.common.logger import logger
from app.domains.document.handlers.node.base import BaseNode
from app.domains.document.handlers.node.utils import download_file_to_firebase_url
from app.domains.document.schemas.state import ParseState


class SplitPDFFilesNode(BaseNode):
    def __init__(self, batch_size=100, save_dir="./data/tmp", test_page=None):
        self.name = "split_pdf_files_node"
        self.batch_size = batch_size
        self.save_dir = save_dir
        self.test_page = test_page

    def _save_split_pdf(
        self, input_doc: pymupdf.Document, start: int, end: int, output_path: str
    ):
        """주어진 범위의 페이지를 새 PDF 파일로 저장하는 함수."""
        try:
            # 페이지 번호 유효성 검사 추가
            num_pages = len(input_doc)
            if not (0 <= start <= end < num_pages):
                logger.error(
                    f"잘못된 페이지 범위: start={start}, end={end}, num_pages={num_pages}"
                )
                # 유효하지 않은 범위에 대한 예외 발생 또는 처리 로직 추가 가능
                raise ValueError(
                    f"Invalid page range: start={start}, end={end}, num_pages={num_pages}"
                )

            logger.info(f"분할 PDF 생성 시작: {output_path} (페이지 {start+1}-{end+1})")
            with pymupdf.open() as output_pdf:
                # 페이지 삽입 (동기 작업)
                output_pdf.insert_pdf(input_doc, from_page=start, to_page=end)
                # 파일 저장 (동기 작업 - I/O 발생)
                output_pdf.save(output_path)
            logger.info(f"분할 PDF 생성 완료: {output_path}")
        except Exception as e:
            # 특정 파일 저장 실패 시 로깅 강화
            logger.error(f"분할 PDF 저장 실패 ({output_path}): {e}", exc_info=True)
            raise

    async def execute(self, state: ParseState) -> AsyncGenerator[ParseState, None]:
        """입력 PDF를 여러 개의 작은 PDF 파일로 분할합니다. Upstage가 지원하는 파일의 페이지 수는 100 페이지 이하입니다."""
        ext = state["ext"]
        filepath = state["filepath"]
        save_dir = self.save_dir
        file_name = state["file_name"]
        if ext == "pdf":
            input_pdf = None
            original_pdf = None

            output_files = []
            try:
                # URL인지 파일 경로인지 확인
                parsed_url = urlparse(filepath)
                is_url = parsed_url.scheme in ("http", "https")

                if is_url:
                    logger.info(f"URL에서 PDF 다운로드 시작: {filepath}")
                    async with (
                        aiohttp.ClientSession() as session,
                        session.get(filepath) as response,
                    ):
                        response.raise_for_status()
                        pdf_content = await response.read()
                        original_pdf = await asyncio.to_thread(
                            pymupdf.open, stream=pdf_content, filetype="pdf"
                        )
                    logger.info(f"URL에서 PDF 다운로드 완료: {len(pdf_content)} bytes")
                else:
                    # 1. 원본 PDF 열기
                    original_pdf = await asyncio.to_thread(pymupdf.open, filepath)
                    logger.info(f"로컬 PDF 파일 열기 완료: {filepath}")

                # 2. PDF 정리 (메모리 내에서 수행)
                logger.info(f"PDF 정리 시작 (메모리): {filepath}")
                cleaned_pdf_bytes = await asyncio.to_thread(
                    original_pdf.tobytes, garbage=4, deflate=True
                )
                await asyncio.to_thread(original_pdf.close)
                logger.info(f"PDF 정리 완료 (메모리): {len(cleaned_pdf_bytes)} bytes")

                # 3. 정리된 PDF를 메모리에서 바로 열기
                input_pdf = await asyncio.to_thread(
                    pymupdf.open, stream=cleaned_pdf_bytes
                )
                num_pages = await asyncio.to_thread(len, input_pdf)
                logger.info(f"정리된 PDF 페이지 수: {num_pages}")

                if self.test_page is not None and self.test_page < num_pages:
                    num_pages = self.test_page
                    logger.info(f"테스트 페이지 제한 적용: {num_pages} 페이지만 처리")

                # 4. PDF 분할 작업 생성
                split_tasks = []
                if is_url:
                    filename = os.path.basename(parsed_url.path)
                    input_file_basename = os.path.splitext(filename)[0]
                else:
                    input_file_basename = os.path.splitext(os.path.basename(filepath))[
                        0
                    ]

                for start_page in range(0, num_pages, self.batch_size):
                    end_page = min(start_page + self.batch_size, num_pages) - 1
                    output_file = (
                        f"{input_file_basename}_{start_page:04d}_{end_page:04d}.pdf"
                    )
                    output_files.append(os.path.join(save_dir, output_file))
                    split_tasks.append(
                        asyncio.to_thread(
                            self._save_split_pdf,
                            input_pdf,
                            start_page,
                            end_page,
                            os.path.join(save_dir, output_file),
                        )
                    )

                # 5. 분할 작업 동시 실행
                await asyncio.gather(*split_tasks)
                logger.info(f"총 {len(output_files)}개의 파일로 분할 완료.")

            except Exception as e:
                logger.error(f"PDF 분할 중 오류 발생: {e}", exc_info=True)
                raise
            finally:
                # 6. PDF 파일 닫기
                if input_pdf:
                    await asyncio.to_thread(input_pdf.close)
                    logger.info("PDF 파일 닫기 완료")

            yield {"split_filepaths": output_files}
        else:
            if filepath.startswith(("http://", "https://")):
                temp_file_path = f"{save_dir}/{file_name}"
                logger.info(f"Downloading file: {filepath} to {temp_file_path}")
                response = await download_file_to_firebase_url(filepath, temp_file_path)
                if response:
                    logger.info(f"File downloaded successfully: {response}")
                    yield {"split_filepaths": [response]}
                else:
                    raise ValueError(f"Failed to download file: {file_name}")
            else:
                logger.info(f"File is not a URL: {filepath}")
                yield {"split_filepaths": [filepath]}
