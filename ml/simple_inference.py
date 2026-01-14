import sys

sys.path.append("../")


import time

from openai import OpenAI
from transformers import HfArgumentParser
from utils.argumentations import (
    DataTrainingArguments,
    ModelArguments,
    OurTrainingArguments,
)

from app.common.logger import logger

# vLLM 서버 설정 (기본값)
VLLM_API_URL = "http://localhost:8000/v1"
VLLM_API_KEY = "EMPTY"  # vLLM은 기본적으로 키가 필요 없음
MODEL_NAME = "vllm_model"  # serve 할 때 지정한 모델 이름 (폴더명)


def main():
    parser = HfArgumentParser(
        (ModelArguments, DataTrainingArguments, OurTrainingArguments)
    )
    if len(sys.argv) == 1:
        model_args, data_args, training_args = parser.parse_args_into_dataclasses(
            args=[]
        )
    else:
        model_args, data_args, training_args = parser.parse_args_into_dataclasses()

    logger.info(f"Connecting to vLLM server at {VLLM_API_URL}...")

    try:
        client = OpenAI(base_url=VLLM_API_URL, api_key=VLLM_API_KEY)
        # 서버 연결 테스트 (모델 리스트 조회)
        models = client.models.list()
        logger.info(f"Connected. Available models: {[m.id for m in models.data]}")
        # 실제 서빙 중인 모델 이름으로 업데이트 (리스트의 첫 번째 모델 사용)
        if models.data:
            global MODEL_NAME
            MODEL_NAME = models.data[0].id
            logger.info(f"Using model: {MODEL_NAME}")

    except Exception as e:
        logger.error(f"Failed to connect to vLLM server: {e}")
        logger.error("Please make sure 'vllm serve' is running.")
        return

    # message_list = [
    #     [
    #         {
    #             "role": "user",
    #             "content": "BMA 공정에서 발생하는 [70012] T4 TIME OVER ALARM의 발생 메커니즘과 근본 원인을 PLC와 AMR 간의 인터페이스 관점에서 상세히 설명해줘.",
    #         }
    #     ],
    #     [
    #         {
    #             "role": "user",
    #             "content": "PUT /api/plc/placecommand API의 기능 정의와 이 API를 호출할 때 필요한 파라미터 구조에 대해 기술 명세서 형식으로 서술해봐.",
    #         }
    #     ],
    #     [
    #         {
    #             "role": "user",
    #             "content": "차상 작업 전 신호 오류(Scenario 3)를 복구할 때, 왜 dock_reset을 먼저 하고 나서 dock_ok를 보내야 하는지 논리적인 이유를 설명해줘.",
    #         }
    #     ],
    #     [
    #         {
    #             "role": "user",
    #             "content": "0.3T AMR(Box)과 1T AMR(Lift)에서 '끼임' 혹은 '센서 오류'가 발생했을 때의 물리적 조치 방법의 차이를 비교해서 설명해줘.",
    #         }
    #     ],
    #     [
    #         {
    #             "role": "user",
    #             "content": "BMA 공정 AMR의 [99999] 터보 부스트 과열 알람에 대해 설명해줘.",
    #         }
    #     ],
    # ]
    # message_list = [
    #     [
    #         {
    #             "role": "user",
    #             "content": "BMA 자동화 시스템의 WEB ACS 운영 로직 및 AMR 전력 관리 아키텍처 전반에 대해 기술 백서 형식으로 상세히 서술하시오.",
    #         },
    #     ],
    #     [
    #         {
    #             "role": "user",
    #             "content": "AMR과 PLC 간의 시계열 동기화(Handshaking) 과정에서 발생하는 타임아웃 에러의 공학적 원인과, 각 제어 단계별 데이터 흐름 및 시스템적 상호작용을 분석하시오.",
    #         },
    #     ],
    #     [
    #         {
    #             "role": "user",
    #             "content": "AMR 상태 조회(AMR Status Retrieval) API의 기술 명세와 데이터 구조 및 관제 시스템 내 활용 방안에 대해 기술 백서 형식으로 상세히 서술하시오.",
    #         },
    #     ],
    #     [
    #         {
    #             "role": "user",
    #             "content": "MCS(Material Control System)를 통한 'PLC 센서 값 갱신(Update PLC Sensor Value) API'의 명세와 활용 시나리오 전반에 대해 기술 백서 형식으로 상세히 서술하시오.",
    #         },
    #     ],
    # ]
    message_list = [
        [
            {
                "role": "user",
                "content": "80023 알림이 뭘 의미하는지 간단하게 말해줘..",
            },
        ],
        # [
        #     {
        #         "role": "user",
        #         "content": "70012 T4 TIME OVER 에러가 났어. 원인이 뭐고 어떻게 조치해야하는지 짧고 간단하게 말해줘.",
        #     },
        # ],
    ]
    logger.info("Sending requests to vLLM...")

    for messages in message_list:
        start_time = time.time()

        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.1,
                max_tokens=2024,
                # vLLM은 기본적으로 효율적인 캐싱을 사용하므로 use_cache 옵션은 불필요 (API에 없음)
                stop=["<|im_end|>", "<|endoftext|>"],
                extra_body={"repetition_penalty": 1.15},
            )

            answer = response.choices[0].message.content
            elapsed = time.time() - start_time

            logger.info(f"Question: {messages[-1]['content']}")
            logger.info(f"Answer: {answer}")
            logger.info(f"Latency: {elapsed:.2f}s")
            logger.info("-" * 100)
            logger.info("\n")

        except Exception as e:
            logger.error(f"Error during inference: {e}")


if __name__ == "__main__":
    main()
