from datetime import datetime
from zoneinfo import ZoneInfo


def get_kst_now() -> datetime:
    return datetime.now(ZoneInfo("Asia/Seoul"))
