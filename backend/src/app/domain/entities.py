from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from app.domain.enums import (
    AttendanceStatus,
    CoursePaymentType,
    CourseType,
    LessonType,
    UserRole,
)


@dataclass
class Organization:
    id: int = field(init=False)
    name: str
    slug: str
    created_by_id: int
    created_at: datetime = field(init=False)
    # Manually set this attribute
    role: UserRole | None = field(init=False, default=None)


@dataclass
class User:
    id: int = field(init=False)
    fullname: str
    email: str
    password: str
    phone: str = ''
    created_at: datetime = field(init=False)


@dataclass
class OrganizationMember:
    id: int = field(init=False)
    organization_id: int
    user_id: int
    user: User | None = field(init=False, default=None)
    role: UserRole
    created_at: datetime = field(init=False)


@dataclass
class Subject:
    id: int = field(init=False)
    organization_id: int
    name: str
    image: str
    description: str


@dataclass
class Course:
    id: int = field(init=False)
    subject_id: int
    subject: Subject | None = field(init=False, default=None)
    type: CourseType
    price: int
    payment_type: CoursePaymentType
    lesson_type: LessonType
    lesson_duration: timedelta
    lessons_count: int | None = None
    duration: timedelta | None = None
    created_at: datetime = field(init=False)
    # Manually set this attribute
    selected_teacher: User | None = None


@dataclass
class CourseTeacher:
    id: int = field(init=False)
    course_id: int
    course: Course | None = field(init=False, default=None)
    teacher_id: int
    teacher: User | None = field(init=False, default=None)
    is_active: bool = True
    created_at: datetime = field(init=False)


@dataclass
class CourseTeacherStudent:
    id: int = field(init=False)
    course_teacher_id: int
    course_teacher: CourseTeacher | None = field(init=False, default=None)
    student_id: int
    student: User | None = field(init=False, default=None)
    created_at: datetime = field(init=False)


@dataclass
class Cabinet:
    id: int = field(init=False)
    address_id: int
    address: Optional['Address'] = field(init=False, default=None)
    number: str


@dataclass
class Address:
    id: int = field(init=False)
    organization_id: int
    address: str
    cabinets: list[Cabinet] = field(default_factory=list)


@dataclass
class Group:
    id: int = field(init=False)
    name: str
    course_id: int
    course: Course | None = field(init=False, default=None)
    max_users_count: int
    default_cabinet_id: int | None = None
    default_cabinet: Cabinet | None = field(init=False, default=None)
    created_at: datetime = field(init=False)


@dataclass
class UserGroup:
    id: int = field(init=False)
    user_id: int
    group_id: int
    is_active: bool = True
    created_at: datetime = field(init=False)


@dataclass
class Lesson:
    id: int = field(init=False)
    conducted_by_id: int
    start_date: datetime
    end_date: datetime
    cabinet_id: int | None = None
    cabinet: Cabinet | None = field(init=False, default=None)
    url: str | None = None
    group_id: int | None = None
    group: Group | None = field(init=False, default=None)
    course_teacher_student_id: int | None = None
    course_teacher_student: CourseTeacherStudent | None = field(
        init=False,
        default=None,
    )
    created_at: datetime = field(init=False)


@dataclass
class Attendance:
    id: int = field(init=False)
    lesson_id: int
    user_id: int
    status: AttendanceStatus
    comment: str = ''


@dataclass
class Feedback:
    id: int = field(init=False)
    author_id: int
    rating: int
    teacher_id: int | None = None
    course_id: int | None = None
    text: str = ''
    is_active: bool = True
    created_at: datetime = field(init=False)


@dataclass
class Payment:
    id: int = field(init=False)
    amount: int
    created_by_id: int
    user_group_id: int | None = None
    lesson_id: int | None = None
    date: datetime = field(init=False)
