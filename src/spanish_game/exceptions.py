from typing import Dict


class InquiryException(Exception):
    def __init__(self, answers: Dict[str, str], message: str, *args, **kwargs):
        self.answers = answers
        self.message = message
        super().__init__(message, *args, **kwargs)


class GameStoppedError(Exception):
    pass
