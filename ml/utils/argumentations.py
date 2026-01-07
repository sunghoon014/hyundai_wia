from dataclasses import dataclass, field
from typing import Optional

from transformers import HfArgumentParser
from trl import SFTConfig


@dataclass
class ModelArguments:
    """Arguments pertaining to which model/config/tokenizer we are going to fine-tune from."""

    model_name_or_path: str = field(
        default="Qwen/Qwen3-4B-Thinking-2507",
        metadata={
            "help": "Path to pretrained model or model identifier from huggingface.co/models"
        },
    )
    lora_r: int = field(
        default=32,
        metadata={
            "help": "학습 할 에폭 수"
            "LLM 학습 시 에폭 수를 1~3으로 줄여서 실험 진행 필요"
        },
    )
    lora_alpha: int = field(
        default=32,
        metadata={
            "help": "학습 할 에폭 수"
            "LLM 학습 시 에폭 수를 1~3으로 줄여서 실험 진행 필요"
        },
    )
    lora_dropout: float = field(
        default=0.0,
        metadata={
            "help": "학습 할 에폭 수"
            "LLM 학습 시 에폭 수를 1~3으로 줄여서 실험 진행 필요"
        },
    )
    lora_bias: str = field(
        default="none",
        metadata={"help": "Bias type for LoRA. 'none' or 'all'. Default: 'none'"},
    )


@dataclass
class DataTrainingArguments:
    """Arguments pertaining to what data we are going to input our model for training and eval."""

    # 학습 데이터 불러오기
    dataset_name: str = field(
        default="./data/step1/final_qwen_conversation_format.json",
        metadata={"help": "The name of the dataset to use."},
    )
    # 검증 데이터 불러오기
    valid_dataset_name: str | None = field(
        default=None,
        metadata={"help": "The name of the dataset to use."},
    )
    # # 토크나이저 설정
    # truncation: bool = field(
    #     default=True,
    #     metadata={
    #         "help": "입력 텍스트가 모델의 최대 허용 길이를 초과하더라도 잘리지 않고 그대로 유지"
    #         "EXAONE maximum context length : 4096"
    #     },
    # )
    # padding: bool = field(
    #     default=False,
    #     metadata={
    #         "help": "DataCollatorForCompletionOnlyLM 을 통해 배치 내에서 가장 긴 시퀀스의 길이에 맞춰 다른 시퀀스들을 패딩"
    #     },
    # )


@dataclass
class OurTrainingArguments(SFTConfig):
    """모델 학습할때 사용되는 하이퍼파라미터 커스텀. SFTConfig를 상속받아 사용."""

    # 기본 학습 설정
    output_dir: str | None = field(
        default="./checkpoints/",
        metadata={"help": "체크포인트와 모델 출력을 저장할 디렉터리 경로"},
    )
    report_to: str | list[str] = field(
        default="wandb",
        metadata={
            "help": "The list of integrations to report the results and logs to."
        },
    )
    max_seq_length: int = field(
        default=4400,  # Step 1: 4313
        metadata={
            "help": "The maximum total input sequence length after tokenization. Sequences longer "
            "than this will be truncated, sequences shorter will be padded."
        },
    )
    do_train: bool = field(
        default=True,
        metadata={"help": "학습을 실행할지 여부"},
    )
    do_eval: bool = field(
        default=False,
        metadata={"help": "평가를 실행할지 여부"},
    )

    # 학습 관련 설정
    gradient_checkpointing: bool = field(
        default=True,
        metadata={
            "help": "메모리 절약을 위해 Gradient Checkpointing 사용 (속도는 약간 느려질 수 있음)"
        },
    )
    fp16: bool = field(
        default=True,
        metadata={"help": "FP16 사용 여부, Mac 사용 시 False"},
    )
    bf16: bool = field(
        default=False,
        metadata={"help": "BF16 사용 여부, Mac 사용 시 True"},
    )
    num_train_epochs: int = field(
        default=3,
        metadata={
            "help": "학습 할 에폭 수"
            "LLM 학습 시 에폭 수를 1~3으로 줄여서 실험 진행 필요"
        },
    )
    # save_strategy: str | None = field(
    #     default="steps",
    #     metadata={"help": "epoch/steps이 끝날때마다 저장"},
    # )
    # eval_strategy: str | None = field(
    #     default="epoch",
    #     metadata={"help": "epoch/steps이 끝날때마다 평가"},
    # )
    # eval_steps: int = field(
    #     default=5,
    #     metadata={"help": "어떤 step에서 저장할지"},
    # )
    # save_steps: int = field(
    #     default=200,
    #     metadata={"help": "어떤 step에서 저장할지"},
    # )
    logging_steps: int = field(default=200)
    # save_total_limit: int = field(
    #     default=2,
    #     metadata={
    #         "help": "가장 좋은 체크포인트 n개만 저장하여 이전 모델을 덮어씌우도록 설정"
    #     },
    # )
    # load_best_model_at_end: bool = field(
    #     default=True,
    #     metadata={"help": "가장 좋은 모델 로드"},
    # )
    per_device_train_batch_size: int = field(
        default=8,
        metadata={
            "help": "학습 중 장치당 배치 크기"
            "GPU 메모리에 따라 줄여서 사용 / 너무 큰 배치는 지양"
        },
    )
    # per_device_eval_batch_size: int = field(
    #     default=1,
    #     metadata={
    #         "help": "평가 중 장치당 배치 크기"
    #         "per_device_eval_batch_size 따라 accuracy 값이 다르게 나옴"
    #         "지정된 batch 내에서 accuracy를 계산해서 그런 것 같은데 근데 1일 때는 어떻게 계산하는 지 모르겠음"
    #     },
    # )
    gradient_accumulation_steps: int = field(
        default=2,
        metadata={
            "help": "그래디언트 누적을 위한 스텝 수"
            "GPU 자원이 부족할 시 배치를 줄이고 누적 수를 늘려 학습"
        },
    )
    learning_rate: int = field(
        default=2e-05,
        metadata={
            "help": "학습률 설정" "학습률 스케줄러(linear, cosine) 사용시 Max 값"
        },
    )
    # 모델 평가 관련
    # metric_for_best_model: str | None = field(
    #     default="eval_loss",
    #     metadata={
    #         "help": "가장 좋은 모델을 평가하기 위한 메트릭 설정"
    #         "본 프로젝트에서는 eval_loss를 기본적으로 사용"
    #     },
    # )
    # greater_is_better: bool = field(
    #     default=False,
    #     metadata={
    #         "help": "설정한 메트릭에 대해 더 큰 값이 더 좋다 혹은 더 작은 값이 더 좋다 설정"
    #         "Accuracy는 True 사용 / eval_loss는 False 사용"
    #     },
    # )
    # Optimizer 설정
    optim: str = field(
        default="adamw_8bit",
        metadata={
            "help": "옵티마이저 설정, 다른 옵티마이저 확인을 위해 아래 url에서 OptimizerNames 확인"
            "Default : adamw_torch / QLoRA 사용시 : paged_adamw_8bit / adamw_8bit"
            "https://github.com/huggingface/transformers/blob/main/src/transformers/training_args.py"
        },
    )
    weight_decay: int = field(
        default=0.001,
        metadata={
            "help": "가중치 감소율 (정규화), 과적합 방지" "0.01 ~ 0.1 정도가 많이 사용"
        },
    )
    max_grad_norm: int = field(
        default=0,
        metadata={
            "help": "그래디언트 클리핑을 위한 최대 노름"
            "1 또는 그 이상의 값으로 설정하는 것이 일반적, 하지만 때에 따라(예를들어 LLM SFT시) 0도 설정 해보길 권장"
        },
    )
    # 스케줄러 설정
    lr_scheduler_type: str | None = field(
        default="cosine",  # cosine_with_restarts
        metadata={"help": "학습률 스케줄러 설정" "cosine_with_restarts"},
    )
    # warmup_steps: int = field(
    #     default=0,
    #     metadata={
    #         "help": "학습률을 워밍업하기 위한 스텝 수"
    #         "전체 학습 스텝 수의 2%~5% 정도로 설정하는 것이 일반적"
    #         "스텝수 = 데이터 개수*에폭수 / 배치사이즈"
    #     },
    # )


if __name__ == "__main__":
    parser = HfArgumentParser(
        (ModelArguments, DataTrainingArguments, OurTrainingArguments)
    )
    model_args, data_args, training_args = parser.parse_args_into_dataclasses()
    print("training_args : ", training_args)
