from app.application.common.id_provider import IdentityProvider
from app.application.repositories.lesson import LessonRepository
from app.application.services.permission import PermissionService
from app.domain.entities import Lesson
from app.domain.enums import UserRole
from app.domain.exceptions import PermissionDeniedError


class GetMyLessons:
    def __init__(
        self,
        lesson_repository: LessonRepository,
        id_provider: IdentityProvider,
        permission_service: PermissionService,
    ):
        self.lesson_repository = lesson_repository
        self.id_provider = id_provider
        self.permission_service = permission_service

    async def __call__(self) -> list[Lesson]:
        user_id = self.id_provider.get_current_user_id()
        role = await self.permission_service.get_current_role()
        if role == UserRole.STUDENT:
            return await self.lesson_repository.get_student_lessons(user_id)
        elif role == UserRole.TEACHER:
            return await self.lesson_repository.get_teacher_lessons(user_id)
        else:
            raise PermissionDeniedError()
