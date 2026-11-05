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


class UnauthorizedError(AppError):
    def __init__(self, detail: Any = "Could not validate credentials.") -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail)
        self.headers = {"WWW-Authenticate": "Bearer"}


class ForbiddenError(AppError):
    def __init__(self, detail: Any = "Not enough permissions.") -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, detail)


class ExternalServiceError(AppError):
    def __init__(self, detail: Any = "An upstream service failed.") -> None:
        super().__init__(status.HTTP_502_BAD_GATEWAY, detail)
