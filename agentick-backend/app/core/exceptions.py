from typing import Any

from fastapi import HTTPException, status


class AppError(HTTPException):
    def __init__(self, status_code: int, detail: Any = None) -> None:
        super().__init__(status_code=status_code, detail=detail)


class NotFoundError(AppError):
    def __init__(self, detail: Any = "Resource not found.") -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail)


class DuplicatedError(AppError):
    def __init__(self, detail: Any = "Resource already exists.") -> None:
        super().__init__(status.HTTP_409_CONFLICT, detail)
