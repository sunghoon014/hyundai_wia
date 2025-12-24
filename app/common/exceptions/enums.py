from fastapi import status


class StatusCode:
    """Response 상태 코드."""

    HTTP_400 = status.HTTP_400_BAD_REQUEST
    HTTP_401 = status.HTTP_401_UNAUTHORIZED
    HTTP_403 = status.HTTP_403_FORBIDDEN
    HTTP_404 = status.HTTP_404_NOT_FOUND
    HTTP_405 = status.HTTP_405_METHOD_NOT_ALLOWED
    HTTP_422 = status.HTTP_422_UNPROCESSABLE_ENTITY
    HTTP_500 = status.HTTP_500_INTERNAL_SERVER_ERROR
