"""토큰 계산 관련 Context Manager.

OpenAI API의 토큰 계산 로직을 담당합니다.
이미지와 텍스트 모두에 대한 정확한 토큰 계산을 지원합니다.
"""

import math


class TokenLimitError(Exception):
    """토큰 제한 초과 예외."""

    pass


class TokenCounter:
    """OpenAI API의 토큰 계산 규칙을 따라 텍스트와 이미지의 토큰 수를 계산합니다."""

    def __init__(
        self,
        tokenizer,
        max_input_tokens: int = None,
        config: dict = None,
    ):
        """TokenCounter 초기화.

        Args:
            tokenizer: tiktoken 토크나이저 인스턴스
            max_input_tokens: 최대 입력 토큰 수
            config (dict, optional): 토큰 계산 설정. None이면 기본값 사용
        """
        self.tokenizer = tokenizer
        self.max_input_tokens = max_input_tokens

        token_config = config or {}

        # 메시지 토큰 계산 상수
        self.BASE_MESSAGE_TOKENS = token_config.get("base_message_tokens", 4)
        self.FORMAT_TOKENS = token_config.get("format_tokens", 2)

        # 이미지 토큰 계산 설정
        image_config = token_config.get("image", {})
        self.LOW_DETAIL_IMAGE_TOKENS = image_config.get("low_detail_tokens", 85)
        self.HIGH_DETAIL_TILE_TOKENS = image_config.get("high_detail_tile_tokens", 170)
        self.MAX_SIZE = image_config.get("max_size", 2048)
        self.HIGH_DETAIL_TARGET_SHORT_SIDE = image_config.get(
            "high_detail_target_short_side", 768
        )
        self.TILE_SIZE = image_config.get("tile_size", 512)

        # 토큰 사용량 추적
        self.total_input_tokens = 0
        self.total_completion_tokens = 0

    def update_token_count(self, prompt_tokens: int, completion_tokens: int = 0):
        """에이전트의 누적 토큰 사용량을 업데이트하고 로그를 기록합니다."""
        self.total_input_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens

    def check_token_limit(self, messages: list[dict], tools: list[dict] | None = None):
        """API 요청 전 누적 토큰 사용량을 계산하고, 제한을 초과하는 경우 예외를 발생시킵니다."""
        input_tokens = self.count_message_tokens(messages)
        if tools:
            input_tokens += self.count_text(str(tools))

        if (
            self.max_input_tokens
            and (self.total_input_tokens + input_tokens) > self.max_input_tokens
        ):
            error_message = (
                f"Request may exceed input token limit (Current: {self.total_input_tokens}, "
                f"Needed: {input_tokens}, Max: {self.max_input_tokens})"
            )
            raise TokenLimitError(error_message)
        return input_tokens

    def count_text(self, text: str) -> int:
        """텍스트 토큰 수 계산.

        Args:
            text (str): 토큰 수를 계산할 텍스트

        Returns:
            int: 계산된 토큰 수
        """
        if not text:
            return 0
        return len(self.tokenizer.encode(text))

    def count_image(self, image_item: dict) -> int:
        """이미지 토큰 수 계산.

        Args:
            image_item (dict): 이미지 정보를 담은 딕셔너리

        Returns:
            int: 계산된 토큰 수
        """
        detail = image_item.get("detail", "medium")

        if detail == "low":
            return self.LOW_DETAIL_IMAGE_TOKENS

        # high/medium 모두 동일한 계산
        if "dimensions" in image_item:
            width, height = image_item["dimensions"]
            return self._calculate_high_detail_tokens(width, height)

        # 기본값
        return self._calculate_high_detail_tokens(1024, 1024)

    def _calculate_high_detail_tokens(self, width: int, height: int) -> int:
        """고해상도 이미지 토큰 계산.

        Args:
            width (int): 이미지 너비
            height (int): 이미지 높이

        Returns:
            int: 계산된 토큰 수
        """
        # 1. MAX_SIZE 제한
        if max(width, height) > self.MAX_SIZE:
            scale = self.MAX_SIZE / max(width, height)
            width, height = int(width * scale), int(height * scale)

        # 2. 짧은 쪽 스케일링
        scale = self.HIGH_DETAIL_TARGET_SHORT_SIDE / min(width, height)
        scaled_width, scaled_height = int(width * scale), int(height * scale)

        # 3. 타일 계산
        tiles = math.ceil(scaled_width / self.TILE_SIZE) * math.ceil(
            scaled_height / self.TILE_SIZE
        )

        return tiles * self.HIGH_DETAIL_TILE_TOKENS + self.LOW_DETAIL_IMAGE_TOKENS

    def count_content(self, content: str | list) -> int:
        """메시지 내용 토큰 계산.

        Args:
            content (str | list): 텍스트 또는 멀티모달 컨텐츠 리스트

        Returns:
            int: 계산된 토큰 수
        """
        if not content:
            return 0

        if isinstance(content, str):
            return self.count_text(content)

        tokens = 0
        for item in content:
            if isinstance(item, str):
                tokens += self.count_text(item)
            elif isinstance(item, dict):
                if "text" in item:
                    tokens += self.count_text(item["text"])
                elif "image_url" in item:
                    tokens += self.count_image(item)
        return tokens

    def count_message_tokens(self, messages: list[dict]) -> int:
        """메시지 목록 토큰 계산.

        Args:
            messages (list[dict]): 메시지 목록

        Returns:
            int: 계산된 총 토큰 수
        """
        total = self.FORMAT_TOKENS

        for msg in messages:
            tokens = self.BASE_MESSAGE_TOKENS
            tokens += self.count_text(msg.get("role", ""))
            tokens += self.count_content(msg.get("content", ""))

            # tool_calls 처리
            if tool_calls := msg.get("tool_calls"):
                for tc in tool_calls:
                    if func := tc.get("function", {}):
                        tokens += self.count_text(func.get("name", ""))
                        tokens += self.count_text(func.get("arguments", ""))

            tokens += self.count_text(msg.get("name", ""))
            tokens += self.count_text(msg.get("tool_call_id", ""))
            total += tokens

        return total
