# Automatic QA Generation

## 1. 실행 방법

### 1.1. 파이썬 개발 환경 설정

1. [uv](https://docs.astral.sh/uv/) 설치
2. [pyenv](https://github.com/pyenv/pyenv) 또는 uv 활용하여 파이썬 3.12.x 설치
3. uv 활용하여 가상환경 설정

````bash
sudo apt update
sudo apt install tmux
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync --upgrade
hf auth login

4. 가상 환경 실행

```bash
source .venv/bin/activate
````

## 2. 간단한 추론
```bash
cd ml
python merge_for_vllm.py
vllm serve vllm_model --port 8000 --max-model-len 4048 --gpu-memory-utilization 0.9 --enforce-eager
python simple_inference.py
```


## 3. 모델 저장
```bash
python ml/upload_to_hf.py --repo_id "Coxwave/WIA-Qwen3-30B-A3B-Thinking-LoRA-Merged" --private
```
