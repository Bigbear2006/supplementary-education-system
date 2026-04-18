from datetime import datetime, timedelta

from pydantic import BaseModel, ConfigDict

from app.domain.enums import CoursePaymentType, CourseType, LessonType
from app.presentation.api.routers.subject.models import SubjectResponse
from app.presentation.api.routers.user.models import UserResponse


class UpdateCourseRequest(BaseModel):
    subject_id: int
    type: CourseType
    price: int
    payment_type: CoursePaymentType
    lesson_type: LessonType
    lesson_duration: timedelta
    lessons_count: int | None = None
    duration: timedelta | None = None


class CourseResponse(BaseModel):
    id: int
    type: CourseType
    price: int
    payment_type: CoursePaymentType
    lesson_type: LessonType
    lesson_duration: timedelta
    lessons_count: int | None = None
    duration: timedelta | None = None
    selected_teacher: UserResponse | None = None
    model_config = ConfigDict(from_attributes=True)


class DetailCourseResponse(CourseResponse):
    subject: SubjectResponse


class BaseCourseTeacherResponse(BaseModel):
    id: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CourseTeacherResponse(BaseCourseTeacherResponse):
    course_id: int
    teacher_id: int


class DetailCourseTeacherResponse(BaseCourseTeacherResponse):
    course: DetailCourseResponse
    teacher: UserResponse


class BaseCourseTeacherStudentResponse(BaseModel):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CourseTeacherStudentResponse(BaseCourseTeacherStudentResponse):
    course_teacher_id: int
    student_id: int


class DetailCourseTeacherStudentResponse(BaseCourseTeacherStudentResponse):
    course_teacher: CourseTeacherResponse
    student: UserResponse
