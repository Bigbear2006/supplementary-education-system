from collections.abc import Iterator
from contextlib import contextmanager
from datetime import timedelta
from json import JSONDecodeError
from typing import Any

import httpx
from alembic import command
from alembic.config import Config
from app.domain.enums import (
    CoursePaymentType,
    CourseType,
    LessonType,
    UserRole,
)
from app.infrastructure.db.config import DatabaseConfig
from app.infrastructure.di.container import providers
from app.presentation.api.main import create_app
from dishka import AsyncContainer, make_async_container
from fastapi.testclient import TestClient
from httpx import URL
from providers.test_database import TestDatabaseProvider


@contextmanager
def setup_db(db_config: DatabaseConfig) -> Iterator[None]:
    config = Config('alembic.ini')
    section = config.config_ini_section
    config.set_section_option(
        section,
        'SUPERUSER_DATABASE_URL',
        db_config.superuser_url,
    )
    config.set_section_option(
        section,
        'DB_NAME',
        db_config.NAME,
    )
    config.set_section_option(section, 'APP_USER', db_config.APP_USER)

    command.upgrade(config, 'head')
    try:
        yield
    finally:
        command.downgrade(config, 'base')


def get_test_container() -> AsyncContainer:
    return make_async_container(*providers, TestDatabaseProvider())


class CustomTestClient(TestClient):
    def request(
        self,
        method: str,
        url: URL | str,
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
    container = get_test_container()

    db_config = container.get_sync(DatabaseConfig)

    app = create_app(container)

    with (
        CustomTestClient(
            app,
            base_url='http://first.localhost/api/v1',
        ) as client,
        setup_db(db_config),
    ):
        ### USERS
        owner = {
            'fullname': 'ФИО',
            'email': 'owner@gmail.com',
            'phone': '79001234455',
            'password': 'g2md21-n3xd0',
        }
        rsp = client.post('/users/', json=owner)
        assert rsp.json().get('id') == 1

        rsp = client.post('/users/login/', json=owner)
        assert rsp.cookies.get('access')
        owner_cookies = {'access': rsp.cookies['access']}

        rsp = client.get('/users/me/', cookies=owner_cookies)
        assert rsp.json().get('id') == 1

        new_user_phone = '89991234567'
        rsp = client.patch(
            '/users/me/',
            json={'phone': new_user_phone},
            cookies=owner_cookies,
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
            cookies=owner_cookies,
        )
        assert rsp.status_code == 204

        rsp = client.post(
            '/users/login/',
            json={'email': owner['email'], 'password': new_user_password},
        )
        assert rsp.status_code == 204

        ### ORGANIZATIONS
        org_data = {'name': 'first', 'slug': 'first'}
        rsp = client.post(
            '/organizations/',
            json=org_data,
            cookies=owner_cookies,
        )
        assert rsp.json().get('id') == 1

        rsp = client.get(
            '/organizations/current/',
            cookies=owner_cookies,
        )
        assert rsp.json().get('id') == 1

        teacher = {**owner, 'email': 'teacher@gmail.com'}
        rsp = client.post('/users/', json=teacher)
        assert rsp.json().get('id') == 2

        rsp = client.post('/users/login/', json=teacher)
        assert rsp.cookies.get('access')
        teacher_cookies = {'access': rsp.cookies['access']}

        student = {**owner, 'email': 'student@gmail.com'}
        rsp = client.post('/users/', json=student)
        assert rsp.json().get('id') == 3

        rsp = client.post('/users/login/', json=student)
        assert rsp.cookies.get('access')
        student_cookies = {'access': rsp.cookies['access']}

        rsp = client.post(
            '/organizations/current/members/',
            cookies=teacher_cookies,
        )
        assert rsp.json().get('role') == 'STUDENT'

        rsp = client.get(
            '/organizations/current/members/me/',
            cookies=teacher_cookies,
        )
        assert rsp.json().get('role') == 'STUDENT'

        rsp = client.patch(
            '/organizations/current/members/2/',
            json={'role': UserRole.TEACHER},
            cookies=owner_cookies,
        )
        assert rsp.json().get('role') == 'TEACHER'

        rsp = client.post(
            '/organizations/current/members/',
            cookies=student_cookies,
        )
        assert rsp.json().get('role') == 'STUDENT'

        rsp = client.get(
            '/organizations/current/members/',
            cookies=owner_cookies,
        )
        assert rsp.status_code == 200
        assert len(rsp.json()) == 3

        ### ADDRESSES AND CABINETS
        rsp = client.post(
            '/addresses/',
            json={'address': 'Улица Тургеневская, д. 10'},
            cookies=owner_cookies,
        )
        address_id = rsp.json().get('id')
        assert rsp.status_code == 201

        rsp = client.post(
            '/cabinets/',
            json={'address_id': address_id, 'number': '101'},
            cookies=owner_cookies,
        )
        # cabinet_id = rsp.json().get('id')
        assert rsp.status_code == 201

        rsp = client.get('/addresses/', cookies=owner_cookies)
        assert rsp.status_code == 200

        new_address = 'Улицы Большая Садовая'
        rsp = client.patch(
            f'/addresses/{address_id}/',
            json={'address': new_address},
            cookies=owner_cookies,
        )
        assert rsp.status_code == 200
        assert rsp.json().get('address') == new_address

        rsp = client.delete(f'/addresses/{address_id}/', cookies=owner_cookies)
        assert rsp.status_code == 409

        # rsp = client.delete(
        #     f'/cabinets/{cabinet_id}/',
        #     cookies=owner_cookies,
        # )
        # assert rsp.status_code == 204
        #
        # rsp = client.delete(
        #     f'/addresses/{address_id}/',
        #     cookies=owner_cookies,
        # )
        # assert rsp.status_code == 204
        #
        # rsp = client.get('/addresses/', cookies=owner_cookies)
        # assert rsp.status_code == 200
        # assert rsp.json() == []

        # SUBJECTS
        subject = {
            'name': 'Subject',
            'image': 'https://placehold.co/600x400/png',
            'description': 'Subject description',
        }
        rsp = client.post('/subjects/', json=subject, cookies=owner_cookies)
        assert rsp.status_code == 201
        assert rsp.json().get('id') == 1

        subject['name'] = 'Updated Subject Name'
        rsp = client.patch(
            '/subjects/1/',
            json={'name': subject['name']},
            cookies=owner_cookies,
        )
        assert rsp.status_code == 200
        assert rsp.json().get('name') == subject['name']

        rsp = client.get('/subjects/')
        assert len(rsp.json()) == 1

        # rsp = client.delete(f'/subjects/1/', cookies=owner_cookies)
        # assert rsp.status_code == 204

        # rsp = client.get('/subjects/')
        # assert len(rsp.json()) == 0

        # COURSES
        course = {
            'subject_id': 1,
            'type': CourseType.GROUP,
            'price': 1000,
            'payment_type': CoursePaymentType.EVERY_LESSON,
            'lesson_type': LessonType.ONLINE,
            'lesson_duration': timedelta(minutes=60).total_seconds(),
            'duration': timedelta(days=30).total_seconds(),
        }
        rsp = client.post('/courses/', json=course, cookies=owner_cookies)
        assert rsp.status_code == 201

        course['price'] = 2000
        rsp = client.put('/courses/1/', json=course, cookies=owner_cookies)
        assert rsp.status_code == 200
        assert rsp.json().get('price') == 2000

        rsp = client.get('/courses/')
        assert len(rsp.json()) == 1

        rsp = client.post('/courses/1/teachers/2/', cookies=owner_cookies)
        assert rsp.status_code == 201

        rsp = client.post(
            '/courses/1/teachers/2/students/me/',
            cookies=student_cookies,
        )
        assert rsp.status_code == 201

        rsp = client.get('/courses/1/teachers/', cookies=owner_cookies)
        assert len(rsp.json()) == 1

        rsp = client.get('/courses/my/', cookies=teacher_cookies)
        assert len(rsp.json()) == 1

        rsp = client.get('/courses/my/', cookies=student_cookies)
        assert len(rsp.json()) == 1

        rsp = client.get(
            '/courses/1/teachers/2/students/',
            cookies=owner_cookies,
        )
        assert len(rsp.json()) == 1

        rsp = client.delete('/courses/1/teachers/2/', cookies=owner_cookies)
        assert rsp.status_code == 204

        # GROUPS
        group = {
            'name': 'Group 1',
            'course_id': 1,
            'max_users_count': 15,
            'default_cabinet_id': 1,
        }
        rsp = client.post('/groups/', json=group, cookies=owner_cookies)
        assert rsp.status_code == 201
        assert rsp.json().get('name') == group['name']

        group['name'] = 'Group 1 Updated'
        rsp = client.put('/groups/1/', json=group, cookies=owner_cookies)
        assert rsp.json().get('name') == group['name']

        rsp = client.get('/groups/', cookies=owner_cookies)
        assert rsp.status_code == 200
        assert len(rsp.json()) == 1

        rsp = client.get('/groups/1/', cookies=owner_cookies)
        assert rsp.json().get('name') == group['name']

        rsp = client.post('/groups/1/users/3/', cookies=owner_cookies)
        assert rsp.status_code == 204

        rsp = client.get('/groups/1/users/', cookies=owner_cookies)
        assert rsp.status_code == 200
        assert len(rsp.json()) == 1

        # rsp = client.delete('/groups/1/users/3/', cookies=owner_cookies)
        # assert rsp.status_code == 204
        #
        # rsp = client.get('/groups/1/users/', cookies=owner_cookies)
        # assert rsp.status_code == 200
        # assert len(rsp.json()) == 0

        ### LESSONS
        lesson = {
            'conducted_by_id': 2,
            'start_date': '2026-04-18 17:00:00',
            'end_date': '2026-04-18 18:00:00',
            'cabinet_id': 1,
            'group_id': 1,
        }
        rsp = client.post('/lessons/', json=lesson, cookies=owner_cookies)
        assert rsp.status_code == 201

        rsp = client.get('/lessons/my/', cookies=student_cookies)
        assert rsp.status_code == 200
        assert len(rsp.json()) == 1

        rsp = client.get('/lessons/my/', cookies=teacher_cookies)
        assert rsp.status_code == 200
        assert len(rsp.json()) == 1


if __name__ == '__main__':
    main()
