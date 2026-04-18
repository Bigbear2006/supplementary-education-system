from datetime import date
from typing import Protocol

from app.domain.entities import Lesson


class LessonRepository(Protocol):
    async def create(self, lesson: Lesson) -> Lesson:
        pass

    async def get_by_date_range(
        self,
        start_date: date,
        end_date: date,
    ) -> list[Lesson]:
        pass

    async def get_student_lessons(self, user_id: int) -> list[Lesson]:
        pass

    async def get_teacher_lessons(self, user_id: int) -> list[Lesson]:
        pass
