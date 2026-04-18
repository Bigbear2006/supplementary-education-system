from datetime import date
from typing import cast

from sqlalchemy import Select, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.application.repositories.lesson import LessonRepository
from app.domain.entities import (
    Cabinet,
    Course,
    CourseTeacher,
    CourseTeacherStudent,
    Group,
    Lesson,
)
from app.infrastructure.db.models import (
    course_teacher_students_table,
    lessons_table,
    user_groups_table,
)
from app.infrastructure.db.repositories.base import create


class LessonRepositoryImpl(LessonRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, lesson: Lesson) -> Lesson:
        return await create(self.session, lesson)

    async def get_by_date_range(
        self,
        start_date: date,
        end_date: date,
    ) -> list[Lesson]:
        stmt = select(Lesson).where(
            lessons_table.c.start_date >= start_date,
            lessons_table.c.end_date <= end_date,
        )
        rows = await self.session.scalars(stmt)
        return cast(list[Lesson], rows.all())

    async def get_student_lessons(self, user_id: int) -> list[Lesson]:
        stmt = (
            _set_lessons_joins(select(Lesson))
            .join(
                user_groups_table,
                lessons_table.c.group_id == user_groups_table.c.group_id,
                isouter=True,
            )
            .join(
                course_teacher_students_table,
                lessons_table.c.course_teacher_student_id
                == course_teacher_students_table.c.id,
                isouter=True,
            )
            .where(
                or_(
                    course_teacher_students_table.c.student_id == user_id,
                    user_groups_table.c.user_id == user_id,
                ),
            )
        )
        rows = await self.session.scalars(stmt)
        return cast(list[Lesson], rows.unique().all())

    async def get_teacher_lessons(self, user_id: int) -> list[Lesson]:
        stmt = _set_lessons_joins(select(Lesson)).where(
            lessons_table.c.conducted_by_id == user_id,
        )
        rows = await self.session.scalars(stmt)
        return cast(list[Lesson], rows.unique().all())


def _set_lessons_joins(stmt: Select[tuple[Lesson]]) -> Select[tuple[Lesson]]:
    return (
        stmt.options(joinedload(Lesson.cabinet).joinedload(Cabinet.address))  # type: ignore[arg-type]
        .options(
            joinedload(Lesson.group)  # type: ignore[arg-type]
            .joinedload(Group.course)  # type: ignore[arg-type]
            .joinedload(Course.subject),  # type: ignore[arg-type]
        )
        .options(
            joinedload(Lesson.course_teacher_student).options(  # type: ignore[arg-type]
                joinedload(CourseTeacherStudent.student),  # type: ignore[arg-type]
                joinedload(CourseTeacherStudent.course_teacher).options(  # type: ignore[arg-type]
                    joinedload(CourseTeacher.course),  # type: ignore[arg-type]
                    joinedload(CourseTeacher.teacher),  # type: ignore[arg-type]
                ),
            ),
        )
    )
