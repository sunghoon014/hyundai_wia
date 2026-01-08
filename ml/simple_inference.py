import os
import sys

from unsloth import FastLanguageModel  # isort: skip

from datasets import Dataset

sys.path.append("../")

import random

import numpy as np
import torch
from transformers import HfArgumentParser
from trl import SFTTrainer
from utils.argumentations import (
    DataTrainingArguments,
    ModelArguments,
    OurTrainingArguments,
)
from utils.util import formatting_prompts_func, load_json

from app.common.logger import logger

SEED = 104
# WandB 프로젝트 설정
os.environ["WANDB_PROJECT"] = "hyundai_wia"

random.seed(SEED)  # python random seed 고정
np.random.seed(SEED)  # numpy random seed 고정
torch.manual_seed(SEED)  # torch random seed 고정
torch.cuda.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False


def main():
    torch.cuda.empty_cache()
    parser = HfArgumentParser(
        (ModelArguments, DataTrainingArguments, OurTrainingArguments)
    )
    model_args, data_args, training_args = parser.parse_args_into_dataclasses()
    logger.info("Load Arguments Successfully")

    # 모델 초기화
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name="./checkpoints/checkpoint-40",
        max_seq_length=training_args.max_seq_length,
        load_in_4bit=True,
        load_in_8bit=False,
    )
    FastLanguageModel.for_inference(model)

    message_list = [
        [
            {
                "role": "user",
                "content": "BMA 공정에서 발생하는 [70012] T4 TIME OVER ALARM의 발생 메커니즘과 근본 원인을 PLC와 AMR 간의 인터페이스 관점에서 상세히 설명해줘.",
            }
        ],
        [
            {
                "role": "user",
                "content": "PUT /api/plc/placecommand API의 기능 정의와 이 API를 호출할 때 필요한 파라미터 구조에 대해 기술 명세서 형식으로 서술해봐.",
            }
        ],
        [
            {
                "role": "user",
                "content": "차상 작업 전 신호 오류(Scenario 3)를 복구할 때, 왜 dock_reset을 먼저 하고 나서 dock_ok를 보내야 하는지 논리적인 이유를 설명해줘.",
            }
        ],
        [
            {
                "role": "user",
                "content": "0.3T AMR(Box)과 1T AMR(Lift)에서 '끼임' 혹은 '센서 오류'가 발생했을 때의 물리적 조치 방법의 차이를 비교해서 설명해줘.",
            }
        ],
        [
            {
                "role": "user",
                "content": "BMA 공정 AMR의 [99999] 터보 부스트 과열 알람에 대해 설명해줘.",
            }
        ],
    ]

    # 배치 처리를 위해 padding_side를 left로 설정 (생성 시 필수)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"

    texts = [
        tokenizer.apply_chat_template(
            msg,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        for msg in message_list
    ]

    # 배치 토크나이징
    inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True).to(
        "cuda"
    )

    logger.info("Generating responses in batch...")
    outputs = model.generate(
        **inputs,
        max_new_tokens=512,
        temperature=0.7,
        top_p=0.8,
        top_k=20,
        use_cache=True,
    )

    # 입력 부분 제외하고 생성된 부분만 디코딩
    generated_ids = outputs[:, inputs.input_ids.shape[1] :]
    decoded_outputs = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)

    for i, (msg, response) in enumerate(
        zip(message_list, decoded_outputs, strict=False)
    ):
        logger.info(f"Question: {msg[-1]['content']}")
        logger.info(f"Answer: {response}")
        logger.info("-" * 100)
        logger.info("\n")


if __name__ == "__main__":
    main()
