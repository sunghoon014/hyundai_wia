from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class ProjectConfig(BaseSettings):
    """프로젝트 경로 관련 설정을 관리합니다.

    Attributes:
        root (str): 프로젝트 루트 경로
    """

    root: str

    class Config:
        env_prefix = "PROJECT_"


class OpenAIConfig(BaseSettings):
    """OpenAI API 설정을 관리합니다.

    Attributes:
        api_key (str): OpenAI API 키
        embedding_model (str): 임베딩 모델 이름
    """

    api_key: str
    embedding_model: str

    class Config:
        env_prefix = "OPENAI_"


class MongoSettings(BaseSettings):
    """MongoDB 설정을 관리합니다.

    Attributes:
        db_url (str): MongoDB 데이터베이스 URL
        db_name (str): MongoDB 데이터베이스 이름
    """

    db_url: str
    db_name: str

    class Config:
        env_prefix = "MONGO_"


class OpenRouterConfig(BaseSettings):
    """OpenRouter API 설정을 관리합니다.

    Attributes:
        api_key (str): OpenRouter API 키
    """

    api_key: str

    class Config:
        env_prefix = "OPENROUTER_"


class UpstageConfig(BaseSettings):
    """Upstage API 설정을 관리합니다.

    Attributes:
        api_key (str): Upstage API 키
    """

    api_key: str

    class Config:
        env_prefix = "UPSTAGE_"


class LangfuseConfig(BaseSettings):
    """Langfuse API 설정을 관리합니다.

    Attributes:
        api_key (str): Langfuse API 키
    """

    host: str
    public_key: str
    secret_key: str

    class Config:
        env_prefix = "LANGFUSE_"


class EnvConfig(BaseSettings):
    """전체 환경 설정을 통합 관리하는 메인 설정 클래스입니다.

    각 서비스별 설정을 하위 설정 클래스로 구성하여 관리합니다.

    Attributes:
        project (ProjectConfig): 프로젝트 설정
        openai (OpenAIConfig): OpenAI API 설정
        anthropic (AnthropicConfig): Anthropic API 설정
        mysql (MySQLConfig): MySQL 데이터베이스 설정
        mongo (MongoSettings): MongoDB 설정
        openrouter (OpenRouterConfig): OpenRouter API 설정
        brave (BraveConfig): Brave API 설정
    """

    project: ProjectConfig = ProjectConfig()
    openai: OpenAIConfig = OpenAIConfig()
    mongo: MongoSettings = MongoSettings()
    openrouter: OpenRouterConfig = OpenRouterConfig()
    upstage: UpstageConfig = UpstageConfig()
    langfuse: LangfuseConfig = LangfuseConfig()
