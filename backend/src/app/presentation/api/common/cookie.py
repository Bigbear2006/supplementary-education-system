from fastapi import Response
from fastapi.security import APIKeyCookie

cookie_scheme = APIKeyCookie(name='access')


def set_access_cookie(response: Response, access: str) -> None:
    response.set_cookie(
        'access',
        access,
        # domain='localhost.ru',
        secure=True,
        httponly=True,
        samesite='none',
    )


def set_refresh_cookie(response: Response, refresh: str) -> None:
    response.set_cookie(
        'refresh',
        refresh,
        path='/api/v1/user/refresh-token/',
        # domain='localhost.ru',
        secure=True,
        httponly=True,
        samesite='none',
    )
