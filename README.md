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

4. 가상 환경 실행

```bash
source .venv/bin/activate
````

### 1.2. 환경변수 설정

1. 개발 환경 정의

   - 로컬 환경
     - `backbone/app/config/local.yaml` 파일 설정
     - `.env` 파일 안에서 `ENV` 변수를 `local`으로 설정
   - 운영 환경
     - `backbone/app/config/prod.yaml` 파일 설정
     - `.env` 파일 안에서 `ENV` 변수를 `prod`으로 설정

2. 로그 레벨 설정

- `.env` 파일 안에서 `LOG_LEVEL` 변수를 설정

3. 프로젝트 루트 경로 설정

- `.env` 파일 안에서 `PROJECT_ROOT` 변수를 설정

4. Full Example

```text
# .env

ENV=local or prod
LOG_LEVEL=DEBUG or INFO or WARNING or ERROR
PROJECT_ROOT=/path/to/backbone_project
...
```

> 현재는 개발 편의를 위해 local.yaml만 사용. 추후 환경별 설정값 분리 필요

### 1.3. Milvus(Standalone) 설치

> PoC 단계이므로 검색해야 할 데이터가 적어 self-hosted Milvus 사용.

- [Milvus Standalone Docker 설치 가이드](https://milvus.io/docs/install_standalone-docker.md)

### 1.4. 실행

- 기본 실행

```bash
# 명령형 인자(`-p`, `--port`)로 포트 설정
# 만약 설정하지 않으면 기본값으로 8000 포트 사용됨.
python -m main
```

## 2. 간단한 추론
```bash
python ml/merge_for_vllm.py
vllm serve vllm_model --port 8000
python ml/simple_inference.py
```
