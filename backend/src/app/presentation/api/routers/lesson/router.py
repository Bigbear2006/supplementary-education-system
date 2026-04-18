from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from app.application.use_cases.lesson import (
    CreateLesson,
    CreateLessonDTO,
    GetMyLessons,
)
from app.presentation.api.routers.lesson.models import (
    DetailLessonResponse,
    LessonResponse,
)

lesson_router = APIRouter(
    prefix='/lessons',
    route_class=DishkaRoute,
    tags=['lessons'],
)


@lesson_router.post('/', status_code=201)
async def create_lesson_router(
    data: CreateLessonDTO,
    create_lesson: FromDishka[CreateLesson],
) -> LessonResponse:
    lesson = await create_lesson(data)
    return LessonResponse.model_validate(lesson)


@lesson_router.get('/my/')
async def get_my_lessons_router(
    get_my_lessons: FromDishka[GetMyLessons],
) -> list[DetailLessonResponse]:
    lessons = await get_my_lessons()
    return [DetailLessonResponse.model_validate(lesson) for lesson in lessons]
