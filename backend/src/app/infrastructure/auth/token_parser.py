from fastapi import Request

from app.domain.exceptions import NotAuthenticatedError


class JWTTokenParser:
    def __init__(self, request: Request) -> None:
        self.request = request

    def parse(self) -> str:
        access = self.request.cookies.get('access')
        if not access:
            raise NotAuthenticatedError()
        return access
