from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.presentation.api.routers.cabinet.models import DetailCabinetResponse
from app.presentation.api.routers.course.models import (
    DetailCourseTeacherStudentResponse,
)
from app.presentation.api.routers.group.models import DetailGroupResponse


class BaseLessonResponse(BaseModel):
    id: int
    conducted_by_id: int
    start_date: datetime
    end_date: datetime
    url: str | None = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class LessonResponse(BaseLessonResponse):
    cabinet_id: int | None = None
    group_id: int | None = None
    course_teacher_student_id: int | None = None


class DetailLessonResponse(BaseLessonResponse):
    cabinet: DetailCabinetResponse | None = None
    group: DetailGroupResponse | None = None
    course_teacher_student: DetailCourseTeacherStudentResponse | None = None
