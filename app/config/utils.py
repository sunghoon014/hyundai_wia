import os

from dependency_injector.providers import Configuration

from app.config.env_config import EnvConfig


def init_config(config: Configuration) -> None:
    """설정을 초기화합니다.

    환경변수와 YAML 파일의 설정을 주입합니다.

    Args:
        config (Configuration): 설정을 저장할 Configuration 객체
    """
    # 환경변수 설정값 주입
    init_env_config(config)

    # yaml 설정값 주입
    init_yaml_config(config)


def init_yaml_config(config: Configuration) -> None:
    """YAML 설정 파일을 로드하여 설정을 초기화합니다.

    ENV 환경변수에 따라 다른 설정 파일을 로드하고,
    공통 프롬프트 설정도 주입합니다.

    Args:
        config (Configuration): 설정을 저장할 Configuration 객체

    Raises:
        ValueError: ENV 환경변수가 설정되지 않은 경우
    """
    if not (env := os.environ.get("ENV")):
        raise ValueError("ENV is not set")

    yaml_path = os.path.join(config.project.root(), "app", "config", f"{env}.yaml")
    prompt_path = os.path.join(config.project.root(), "app", "config", "prompts.yaml")

    # validation
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"YAML Config file not found: {yaml_path}")
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"Prompt Config file not found: {prompt_path}")

    config.from_yaml(yaml_path)
    config.from_yaml(prompt_path)


def init_env_config(config: Configuration) -> None:
    """환경변수에서 설정을 로드하여 초기화합니다.

    Args:
        config (Configuration): 설정을 저장할 Configuration 객체
    """
    config.from_pydantic(EnvConfig())
