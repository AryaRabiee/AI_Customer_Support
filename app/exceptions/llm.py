from .base import AppError


class LLMError(AppError):
    pass


class LLMTimeoutError(LLMError):
    pass

class InvalidDecisionError(LLMError):
    pass