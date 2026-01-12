import json
import re
from pathlib import Path
from typing import Any


def parse_json(text: str):
    """Parses a JSON string."""
    match = re.search(r"```json\s*([\s\S]*?)\s*```", text)
    json_string = match.group(1).strip() if match else text
    return json.loads(json_string)


def load_json(filepath: str | Path, encoding: str = "utf-8") -> dict[str, Any]:
    """파일에서 JSON 데이터를 불러옵니다.

    Args:
        filepath (str | Path): 불러올 파일 경로
        encoding (str): 파일 인코딩 (기본값: "utf-8")

    Returns:
        dict[str, Any]: 파일에서 읽은 JSON 데이터 (dict)
    """
    path = Path(filepath)
    with open(path, encoding=encoding) as f:
        return json.load(f)


def formatting_prompts_func(examples: dict[str, Any], tokenizer) -> dict[str, Any]:
    convos = examples["conversation"]
    texts = [
        tokenizer.apply_chat_template(
            convo, tokenize=False, add_generation_prompt=False
        )
        for convo in convos
    ]
    return {"text": texts}
