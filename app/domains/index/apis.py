from fastapi import APIRouter

from app.domains import API_VERSION
from app.domains.index.schemas import APIInfoResponse, HealthCheckResponse

index_router = APIRouter(tags=["Index"])


@index_router.get(
    path="/", name="Application health checker", response_model=HealthCheckResponse
)
async def health_check_api():
    """애플리케이션 상태 검사 API입니다.

    애플리케이션이 정상적으로 작동 중인지 확인하는 엔드포인트입니다.
    로드밸런서나 모니터링 시스템에서 사용됩니다.

    Returns:
        HealthCheckResponse: 애플리케이션 상태 정보
    """
    return HealthCheckResponse()


@index_router.get(
    path="/api_info",
    summary="API Version",
    description="Return API version",
    response_model=APIInfoResponse,
)
async def get_api_info_api():
    """API 정보 조회 API입니다.

    현재 애플리케이션의 API 버전 정보를 반환합니다.
    클라이언트에서 API 호환성을 확인하는 데 사용됩니다.

    Returns:
        APIInfoResponse: API 상태 및 버전 정보
    """
    return APIInfoResponse(status="ok", api_version=API_VERSION)


# NOTE: Open-web-ui 활용할 때 필요한 API
@index_router.get(path="/models", name="Open-web-ui 호환용 API", response_model=dict)
async def models() -> dict:
    """OpenWebUI 호환성을 위한 모델 목록 API입니다.

    OpenWebUI 인터페이스와 호환되도록 모델 목록을 반환합니다.
    이 엔드포인트는 외부 인터페이스와의 호환성을 위해 제공됩니다.

    Returns:
        dict: OpenWebUI 호환 형식의 모델 목록
    """
    return {
        "object": "list",
        "data": [
            {
                "id": "AX Boilerplate",
                "object": "model",
                "created": 999999,
                "owned_by": "ax",
            },
        ],
    }
