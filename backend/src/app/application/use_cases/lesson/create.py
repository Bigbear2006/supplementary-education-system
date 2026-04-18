from dataclasses import asdict, dataclass
from datetime import datetime

from app.application.common.uow import UnitOfWork
from app.application.repositories.group import GroupRepository
from app.application.repositories.lesson import LessonRepository
from app.application.services.permission import PermissionService
from app.domain.entities import Lesson
from app.domain.exceptions import DefaultCabinetIsNotSetError


@dataclass
class CreateLessonDTO:
    conducted_by_id: int
    start_date: datetime
    end_date: datetime
    cabinet_id: int | None = None
    url: int | None = None
    group_id: int | None = None
    course_teacher_student_id: int | None = None


class CreateLesson:
    def __init__(
        self,
        lesson_repository: LessonRepository,
        group_repository: GroupRepository,
        permission_service: PermissionService,
        uow: UnitOfWork,
    ) -> None:
        self.lesson_repository = lesson_repository
        self.group_repository = group_repository
        self.permission_service = permission_service
        self.uow = uow

    async def __call__(self, data: CreateLessonDTO) -> Lesson:
        await self.permission_service.ensure_admin_or_more()

        if not data.cabinet_id:
            if not data.group_id:
                raise DefaultCabinetIsNotSetError()

            group = await self.group_repository.get_by_id(data.group_id)
            if not group.default_cabinet_id:
                raise DefaultCabinetIsNotSetError()

            data.cabinet_id = group.default_cabinet_id

        async with self.uow:
            lesson = Lesson(**asdict(data))
            return await self.lesson_repository.create(lesson)
