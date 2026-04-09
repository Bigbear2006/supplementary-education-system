from json import JSONDecodeError
from typing import Any

import httpx
from alembic import command
from alembic.config import Config
from app.domain.enums import UserRole
from app.infrastructure.db.config import DatabaseConfig
from app.presentation.api.main import create_app
from fastapi.testclient import TestClient


def setup_db() -> None:
    db_config = DatabaseConfig(NAME='test')
    config = Config('alembic.ini')
    section = config.config_ini_section
    config.set_section_option(
        section,
        'SUPERUSER_DATABASE_URL',
        db_config.superuser_url,
    )
    command.downgrade(config, 'base')
    command.upgrade(config, 'head')


def headers(access_token: str = '') -> dict[str, Any]:
    return {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
    }


class CustomTestClient(TestClient):
    def request(
        self,
        method: str,
        url: httpx._types.URLTypes,
        **kwargs: Any,
    ) -> httpx.Response:
        rsp = super().request(method, url, **kwargs)

        try:
            data = rsp.json()
        except JSONDecodeError:
            data = ''

        print(f'{rsp.status_code} {method} {url}\n{data}\n')
        return rsp


def register(
    client: TestClient,
    fullname: str,
    email: str,
    phone: str,
    password: str,
) -> None:
    _data = {
        'fullname': fullname,
        'email': email,
        'phone': phone,
        'password': password,
    }
    rsp = client.post('/users/', json=_data)
    data = rsp.json()
    assert data.get('fullname') == fullname
    assert data.get('email') == email
    assert data.get('phone') == phone


def main() -> None:
    setup_db()

    app = create_app()
    with CustomTestClient(app, base_url='http://localhost/api/v1') as client:
        ### USERS
        owner = {
            'fullname': 'ФИО',
            'email': 'morozm982@gmail.com',
            'phone': '79381298115',
            'password': 'g2md21-n3xd0',
        }
        rsp = client.post('/users/', json=owner)
        assert rsp.json().get('id') == 1

        rsp = client.post('/users/login/', json=owner)
        owner_access = rsp.cookies.get('access')
        assert owner_access
        owner_cookies = {'access': owner_access}

        rsp = client.get('/users/me/', cookies=owner_cookies)
        assert rsp.json().get('id') == 1

        access_token = ''
        return

        new_user_phone = '89991234567'
        rsp = client.patch(
            '/users/me/',
            json={'phone': new_user_phone},
            headers=headers(access_token),
        )
        assert rsp.json().get('fullname') == owner['fullname']
        assert rsp.json().get('phone') == new_user_phone

        new_user_password = 'm92f4032f4u'
        rsp = client.patch(
            '/users/me/change-password/',
            json={
                'old_password': owner['password'],
                'new_password': new_user_password,
            },
            headers=headers(access_token),
        )
        assert rsp.status_code == 204

        rsp = client.post(
            '/users/login/',
            json={'email': owner['email'], 'password': new_user_password},
        )
        access_token = rsp.json().get('access_token')
        assert access_token

        ### ORGANIZATIONS
        org_data = {'name': 'first', 'slug': 'first'}
        rsp = client.post(
            '/organizations/',
            json=org_data,
            headers=headers(access_token),
        )
        assert rsp.json().get('id') == 1

        rsp = client.get(
            '/organizations/current/',
            headers=headers(access_token),
        )
        assert rsp.json().get('id') == 1

        user_data_2 = {**owner, 'email': 'mororzm983@gmail.com'}
        rsp = client.post('/users/', json=user_data_2)
        assert rsp.json().get('id') == 2

        rsp = client.post('/users/login/', json=user_data_2)
        access_token_2 = rsp.json().get('access_token')
        assert access_token_2

        rsp = client.post(
            '/organizations/current/members/',
            headers=headers(access_token_2),
        )
        assert rsp.json().get('role') == 'STUDENT'

        rsp = client.get(
            '/organizations/current/members/me/',
            headers=headers(access_token_2),
        )
        assert rsp.json().get('role') == 'STUDENT'

        rsp = client.patch(
            '/organizations/current/members/2/',
            json={'role': UserRole.TEACHER},
            headers=headers(access_token),
        )
        assert rsp.json().get('role') == 'TEACHER'

        rsp = client.get(
            '/organizations/current/members/',
            headers=headers(access_token),
        )
        assert rsp.status_code == 200
        assert len(rsp.json()) == 2

        ### ADDRESSES AND CABINETS
        owner_headers = headers(access_token)
        rsp = client.post(
            '/addresses/',
            json={'address': 'Улица Тургеневская, д. 10'},
            headers=owner_headers,
        )
        address_id = rsp.json().get('id')
        assert rsp.status_code == 201

        rsp = client.post(
            '/cabinets/',
            json={'address_id': address_id, 'number': '101'},
            headers=owner_headers,
        )
        cabinet_id = rsp.json().get('id')
        assert rsp.status_code == 201

        rsp = client.get('/addresses/', headers=owner_headers)
        assert rsp.status_code == 200

        new_address = 'Улицы Большая Садовая'
        rsp = client.patch(
            f'/addresses/{address_id}/',
            json={'address': new_address},
            headers=owner_headers,
        )
        assert rsp.status_code == 200
        assert rsp.json().get('address') == new_address

        rsp = client.delete(f'/addresses/{address_id}/', headers=owner_headers)
        assert rsp.status_code == 409

        rsp = client.delete(f'/cabinets/{cabinet_id}/', headers=owner_headers)
        assert rsp.status_code == 204

        rsp = client.delete(f'/addresses/{address_id}/', headers=owner_headers)
        assert rsp.status_code == 204

        rsp = client.get('/addresses/', headers=owner_headers)
        assert rsp.status_code == 200
        assert rsp.json() == []

        # SUBJECTS, COURSES AND GROUPS
        subject = {
            'name': 'Subject',
            'image': 'https://placehold.co/600x400/png',
            'description': 'Subject description',
        }
        rsp = client.post('/subjects/', json=subject, headers=owner_headers)
        assert rsp.status_code == 201


if __name__ == '__main__':
    main()
