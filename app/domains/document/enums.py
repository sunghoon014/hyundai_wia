from enum import Enum


class DocumentProcessingStatus(Enum):
    """Document processing status enum with percentage."""

    PARSING = ("PARSING", 25)
    PREPROCESSING = ("PREPROCESSING", 50)
    INDEXING = ("INDEXING", 100)
    SAVED = ("SAVED", 100)

    def __init__(self, status: str, percentage: int):
        self.status = status
        self.percentage = percentage
