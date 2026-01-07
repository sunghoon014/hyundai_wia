"""Train knowledge model with LoRA. 추후 Unsloth으로 변경 필요."""

import os
import sys

from datasets import Dataset

sys.path.append("../")

import random

import numpy as np
import torch
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    HfArgumentParser,
)
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

    # QLoRA를 위한 BitsAndBytes 설정 (4bit, NF4, Double Quantization)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    # 모델 초기화 (4bit 양자화 적용)
    model = AutoModelForCausalLM.from_pretrained(
        model_args.model_name_or_path,
        quantization_config=bnb_config,
        device_map="auto",
    )

    # k-bit 학습을 위한 모델 전처리 (Gradient Checkpointing 활성화 등)
    model = prepare_model_for_kbit_training(model)
    tokenizer = AutoTokenizer.from_pretrained(model_args.model_name_or_path)

    # LoRA 초기화
    lora_config = LoraConfig(
        r=model_args.lora_r,
        lora_alpha=model_args.lora_alpha,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        lora_dropout=model_args.lora_dropout,
        bias=model_args.lora_bias,
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    logger.info(model.print_trainable_parameters())

    # 데이터셋 로드
    dataset = Dataset.from_list(load_json(data_args.dataset_name))
    dataset = dataset.map(
        formatting_prompts_func,
        batched=True,
        num_proc=4,
        fn_kwargs={"tokenizer": tokenizer},
    )
    logger.info(f"Loaded dataset size: {len(dataset)}")

    # 모델 학습
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        eval_dataset=None,
        peft_config=lora_config,
        args=training_args,
    )

    trainer_stats = trainer.train()
    logger.info(trainer_stats)

    trainer.save_model(training_args.output_dir)
    logger.info(f"Saved model to {training_args.output_dir}")


if __name__ == "__main__":
    main()
