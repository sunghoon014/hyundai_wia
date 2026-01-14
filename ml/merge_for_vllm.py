import sys

sys.path.append("../")
from unsloth import FastLanguageModel  # isort: skip
from transformers import HfArgumentParser
from utils.argumentations import (
    DataTrainingArguments,
    ModelArguments,
    OurTrainingArguments,
)

from app.common.logger import logger


def main():
    parser = HfArgumentParser(
        (ModelArguments, DataTrainingArguments, OurTrainingArguments)
    )
    # 인자가 없으면 기본값으로 파싱
    if len(sys.argv) == 1:
        model_args, data_args, training_args = parser.parse_args_into_dataclasses(
            args=[]
        )
    else:
        model_args, data_args, training_args = parser.parse_args_into_dataclasses()

    # 병합할 체크포인트 경로 (필요시 수정)
    checkpoint_path = "./checkpoints/checkpoint-162"
    output_dir = "vllm_model"

    logger.info(f"Loading model from {checkpoint_path}...")

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=checkpoint_path,
        max_seq_length=training_args.max_seq_length,
        load_in_4bit=True,  # 병합 전 로드는 4bit로 해도 됨
        trust_remote_code=True,
    )

    logger.info(f"Saving merged model to {output_dir} (16bit)...")

    # vLLM 호환성을 위해 16bit로 병합 저장 (Unsloth 가이드 권장)
    model.save_pretrained_merged(
        output_dir,
        tokenizer,
        save_method="merged_16bit",
    )

    logger.info("Merge complete! You can now run vllm with:")
    logger.info(f"vllm serve {output_dir} --port 8000")


if __name__ == "__main__":
    main()
