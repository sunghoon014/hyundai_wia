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
        model_name=model_args.model_name_or_path,
        max_seq_length=training_args.max_seq_length,
        load_in_4bit=True,
        load_in_8bit=False,
    )
    model = FastLanguageModel.get_peft_model(
        model,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        r=model_args.lora_r,
        lora_alpha=model_args.lora_alpha,
        lora_dropout=model_args.lora_dropout,
        lora_bias="none",
        # [NEW] "unsloth" uses 30% less VRAM, fits 2x larger batch sizes!
        use_gradient_checkpointing="unsloth",  # True or "unsloth" for very long context
        random_state=104,
        use_rslora=False,  # We support rank stabilized LoRA
        loftq_config=None,  # And LoftQ
    )
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
        tokenizer=tokenizer,
        train_dataset=dataset,
        eval_dataset=None,
        args=training_args,
    )
    # MPS issues with pin_memory
    if trainer.args.dataloader_pin_memory and torch.backends.mps.is_available():
        logger.warning("MPS detected, disabling pin_memory for stability.")
        trainer.args.dataloader_pin_memory = False

    trainer_stats = trainer.train()
    logger.info(trainer_stats)

    trainer.save_model(training_args.output_dir)
    logger.info(f"Saved model to {training_args.output_dir}")


if __name__ == "__main__":
    main()
