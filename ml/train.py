import os
import random

import numpy as np
import torch
from datasets import Dataset
from peft import LoraConfig, TaskType
from sentence_transformers import SentenceTransformer, SentenceTransformerTrainer
from transformers import HfArgumentParser
from utils.adapter import DisentangledHead
from utils.argumentations import (
    DataTrainingArguments,
    ModelArguments,
    OurTrainingArguments,
)
from utils.io import load_jsonl
from utils.logger import logger
from utils.loss import CalibrationLoss
from utils.metrics import CalibrationEvaluator

SEED = 104
# WandB 프로젝트 설정
os.environ["WANDB_PROJECT"] = "calibration"

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
    logger.info(f"Training arguments: {training_args}")
    logger.info(f"Model arguments: {model_args}")
    logger.info(f"Data arguments: {data_args}")

    # SentenceTransformer 모델 초기화
    model = SentenceTransformer(model_args.model_name_or_path)
    # 모델의 최대 길이 제한 (8192 -> 1024)
    # 학습 속도 최적화를 위해 제한, 필요 시 조절 가능
    model.max_seq_length = 1024
    logger.info(
        f"SentenceTransformer initialized: {model_args.model_name_or_path} with max_seq_length={model.max_seq_length}"
    )
    # Adapter 초기화
    lora_config = LoraConfig(
        task_type=TaskType.FEATURE_EXTRACTION,
        r=model_args.lora_r,
        lora_alpha=model_args.lora_alpha,
        lora_dropout=model_args.lora_dropout,
    )
    model.add_adapter(lora_config)
    logger.info(f"Adapter initialized: {lora_config}")

    # Disentangled Head 추가
    # 1. 기존 차원 확인 (768 or 1024 ...)
    in_features = model.get_sentence_embedding_dimension()

    # 2. Semantic Dimension 계산 (전체 - Reliability Dimension)
    # 예: 768 - 256 = 512
    # sem_dim = in_features - model_args.rel_dim
    sem_dim = in_features
    rel_dim = in_features

    # 3. Head 초기화
    disentangled_head = DisentangledHead(
        in_features=in_features, sem_dim=sem_dim, rel_dim=rel_dim
    )

    # 4. 모델의 마지막 모듈로 추가
    # SentenceTransformer는 _modules(OrderedDict)를 순서대로 실행함
    model.add_module(str(len(model)), disentangled_head)
    logger.info(
        f"DisentangledHead initialized and attached: in={in_features}, sem={sem_dim}, rel={rel_dim}"
    )

    # # train & eval dataset 초기화
    data = load_jsonl(data_args.dataset_name)
    random.shuffle(data)

    train_data = data[: int(len(data) * 0.9)]
    logger.info(f"Train data sample: {train_data[1]}\n...\n{train_data[-1]}")

    eval_data = data[int(len(data) * 0.9) :]
    logger.info(f"Eval data sample: {eval_data[1]}\n...\n{eval_data[-1]}")

    logger.info(f"Train dataloader: {len(train_data)}")
    logger.info(f"Eval dataloader: {len(eval_data)}")

    # We will convert the list of dicts to a Dataset object properly
    train_dataset = Dataset.from_list(train_data)
    eval_dataset = Dataset.from_list(eval_data)

    # Rename columns to standard names if needed, though custom loss handles keys.
    # But the collator might expect standard keys for text inputs.
    # Standard keys: 'sentence_0', 'sentence_1', ... or 'anchor', 'positive', 'negative'
    # Our data has 'query', 'positive', 'negative'.
    train_dataset = train_dataset.map(
        lambda x: {
            "anchor": x["query"],
            "positive": x["positive"],
            "negative": x["negative"],
            "label": [x["pos_label"], x["neg_label"]],  # Combine into one label column
        },
        remove_columns=train_dataset.column_names,
        keep_in_memory=True,
    ).select_columns(["anchor", "positive", "negative", "label"])

    eval_dataset = eval_dataset.map(
        lambda x: {
            "anchor": x["query"],
            "positive": x["positive"],
            "negative": x["negative"],
            "label": [x["pos_label"], x["neg_label"]],
        },
        remove_columns=eval_dataset.column_names,
        keep_in_memory=True,
    ).select_columns(["anchor", "positive", "negative", "label"])

    # Now we have 'anchor', 'positive', 'negative' (text) and 'label' (list of floats).
    # The default collator should handle 'label' as a label and not tokenize it.

    # # loss_fn 초기화
    loss_fn = CalibrationLoss(
        model=model,
        sem_dim=sem_dim,
        rel_dim=rel_dim,
        rel_lambda=model_args.rel_lambda,
        sem_lambda=model_args.sem_lambda,
        norm_lambda=model_args.norm_lambda,
        orth_lambda=model_args.orth_lambda,
    )
    logger.info(f"Loss function initialized: {loss_fn}")

    # # evaluator 초기화
    # We pass the raw list of dicts or Dataset to the evaluator.
    # CalibrationEvaluator expects dataset to be iterable of dicts with 'query', 'positive', 'negative'
    # eval_dataset (Dataset) works fine with DataLoader in Evaluator
    evaluator = CalibrationEvaluator(
        dataset=eval_dataset,
        loss_fn=loss_fn,
        batch_size=training_args.per_device_eval_batch_size,
        name="calib_eval_",
        show_progress_bar=True,
    )
    logger.info(f"Evaluator initialized: {evaluator}")

    # trainer 초기화
    trainer = SentenceTransformerTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        loss=loss_fn,
        evaluator=evaluator,
        data_collator=None,  # Use default
    )
    # MPS issues with pin_memory
    if trainer.args.dataloader_pin_memory and torch.backends.mps.is_available():
        logger.warning("MPS detected, disabling pin_memory for stability.")
        trainer.args.dataloader_pin_memory = False

    logger.info(f"Trainer initialized: {trainer}")

    # 학습 시작
    trainer.train()
    logger.info(f"Training completed: {trainer.state.global_step}")


if __name__ == "__main__":
    main()
