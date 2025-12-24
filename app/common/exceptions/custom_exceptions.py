from app.common.exceptions.enums import StatusCode


class CustomError(Exception):
    def __init__(self, status_code: int, error_code: str, message: str, ex: Exception):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.ex = ex
        super().__init__(ex)


class ChatSessionNotFoundError(CustomError):
    def __init__(self):
        status_code = StatusCode.HTTP_404
        error_code = "1000"
        exception_detail = "채팅 세션을 찾을 수 없습니다."

        super().__init__(
            status_code=status_code,
            error_code=error_code,
            message=exception_detail,
            ex=Exception(exception_detail),
        )


class UnknownToolError(CustomError):
    def __init__(self):
        status_code = StatusCode.HTTP_500
        error_code = "1001"
        exception_detail = "알 수 없는 MCP 도구가 선택되었습니다."

        super().__init__(
            status_code=status_code,
            error_code=error_code,
            message=exception_detail,
            ex=Exception(exception_detail),
        )


class MessageQueueNeverStoppedError(CustomError):
    def __init__(self):
        status_code = StatusCode.HTTP_500
        error_code = "1002"
        exception_detail = "SSE 메시지 큐가 정상적으로 종료되지 않았습니다."

        super().__init__(
            status_code=status_code,
            error_code=error_code,
            message=exception_detail,
            ex=Exception(exception_detail),
        )


class ToolCallError(CustomError):
    def __init__(self):
        status_code = StatusCode.HTTP_500
        error_code = "1003"
        exception_detail = "MCP 도구 호출에 실패하였습니다."

        super().__init__(
            status_code=status_code,
            error_code=error_code,
            message=exception_detail,
            ex=Exception(exception_detail),
        )


class TaskFailError(CustomError):
    def __init__(self):
        status_code = StatusCode.HTTP_500
        error_code = "1004"
        exception_detail = "작업 수행 중 오류가 발생하였습니다."

        super().__init__(
            status_code=status_code,
            error_code=error_code,
            message=exception_detail,
            ex=Exception(exception_detail),
        )


class ToolError(Exception):
    """Raised when a tool encounters an error."""

    def __init__(self, message):
        self.message = message


class TokenLimitError(Exception):
    """Exception raised when the token limit is exceeded."""
