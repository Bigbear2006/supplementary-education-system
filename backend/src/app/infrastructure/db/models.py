from typing import Any, NewType

from sqlalchemy import (
    BIGINT,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Interval,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import registry, relationship

from app.domain.entities import (
    Address,
    Attendance,
    Cabinet,
    Course,
    CourseTeacher,
    CourseTeacherStudent,
    Feedback,
    Group,
    Lesson,
    Organization,
    OrganizationMember,
    Payment,
    Subject,
    User,
    UserGroup,
)
from app.domain.enums import (
    AttendanceStatus,
    CoursePaymentType,
    CourseType,
    LessonTransferStatus,
    LessonType,
    UserRole,
)

# AsyncSession without app.current_org_id set
RawSession = NewType('RawSession', AsyncSession)

metadata = MetaData()
mapper_registry = registry(metadata=metadata)

user_role_enum = Enum(UserRole, name='user_role')
course_type_enum = Enum(CourseType, name='course_type')
lesson_type_enum = Enum(LessonType, name='lesson_type')
course_payment_type_enum = Enum(CoursePaymentType, name='course_payment_type')
attendance_status_enum = Enum(AttendanceStatus, name='attendance_status')
lesson_transfer_status_enum = Enum(
    LessonTransferStatus,
    name='lesson_transfer_status',
)


def organization_id_fk(nullable: bool = False) -> Column[Any]:
    return Column(
        'organization_id',
        BIGINT,
        ForeignKey('organizations.id'),
        nullable=nullable,
    )


def created_at_column() -> Column[Any]:
    return Column(
        'created_at',
        DateTime(timezone=True),
        nullable=False,
        server_default=text('NOW()'),
    )


organizations_table = Table(
    'organizations',
    metadata,
    Column('id', BIGINT, primary_key=True, autoincrement=True),
    Column('name', String(255), unique=True, nullable=False),
    Column('slug', String(50), unique=True, nullable=False),
    Column('created_by_id', BIGINT, nullable=False),
    created_at_column(),
)

users_table = Table(
    'users',
    metadata,
    Column('id', BIGINT, primary_key=True, autoincrement=True),
    Column('fullname', String(100), nullable=False),
    Column('email', String(150), unique=True, nullable=False),
    Column('phone', String(20), nullable=False, server_default=text("''")),
    Column('password', String(128), nullable=False),
    created_at_column(),
)

organization_members_table = Table(
    'organization_members',
    metadata,
    Column('id', BIGINT, primary_key=True, autoincrement=True),
    organization_id_fk(),
    Column('user_id', BIGINT, ForeignKey('users.id'), nullable=False),
    Column('role', user_role_enum, nullable=False),
    created_at_column(),
    UniqueConstraint('organization_id', 'user_id', name='uq_org_user'),
)

subjects_table = Table(
    'subjects',
    metadata,
    Column('id', BIGINT, primary_key=True),
    organization_id_fk(),
    Column('name', String(255), nullable=False),
    Column('image', Text, nullable=False),
    Column('description', Text, nullable=False, server_default=text("''")),
    created_at_column(),
    UniqueConstraint('organization_id', 'name', name='uq_subjects_org_name'),
)

courses_table = Table(
    'courses',
    metadata,
    Column('id', BIGINT, primary_key=True),
    Column('subject_id', BIGINT, ForeignKey('subjects.id'), nullable=False),
    Column('type', course_type_enum, nullable=False),
    Column('price', Integer, nullable=False),
    Column('payment_type', course_payment_type_enum, nullable=False),
    Column('lesson_type', lesson_type_enum, nullable=False),
    Column('lesson_duration', Interval, nullable=False),
    Column('lessons_count', Integer, nullable=True),
    Column('duration', Interval, nullable=True),
    created_at_column(),
)

course_teachers_table = Table(
    'course_teachers',
    metadata,
    Column('id', BIGINT, primary_key=True),
    Column('course_id', BIGINT, ForeignKey('courses.id'), nullable=False),
    Column('teacher_id', BIGINT, ForeignKey('users.id'), nullable=False),
    Column('is_active', Boolean, nullable=False, server_default=text('true')),
    created_at_column(),
)

course_teacher_students_table = Table(
    'course_teacher_students',
    metadata,
    Column('id', BIGINT, primary_key=True),
    Column(
        'course_teacher_id',
        BIGINT,
        ForeignKey('course_teachers.id'),
        nullable=False,
    ),
    Column('student_id', BIGINT, ForeignKey('users.id'), nullable=False),
    created_at_column(),
)

addresses_table = Table(
    'addresses',
    metadata,
    Column('id', BIGINT, primary_key=True),
    organization_id_fk(),
    Column('address', Text, nullable=False),
)

cabinets_table = Table(
    'cabinets',
    metadata,
    Column('id', BIGINT, primary_key=True),
    Column(
        'address_id',
        BIGINT,
        ForeignKey('addresses.id'),
        nullable=False,
    ),
    Column('number', String(10), nullable=False),
    UniqueConstraint(
        'address_id',
        'number',
        name='uq_cabinets_address_number',
    ),
)

groups_table = Table(
    'groups',
    metadata,
    Column('id', BIGINT, primary_key=True),
    Column('name', String(255), nullable=False),
    Column('course_id', BIGINT, ForeignKey('courses.id'), nullable=False),
    Column(
        'default_cabinet_id',
        BIGINT,
        ForeignKey('cabinets.id'),
        nullable=True,
    ),
    Column('max_users_count', Integer, nullable=False),
    created_at_column(),
)

user_groups_table = Table(
    'user_groups',
    metadata,
    Column('id', BIGINT, primary_key=True),
    Column('user_id', BIGINT, ForeignKey('users.id'), nullable=False),
    Column('group_id', BIGINT, ForeignKey('groups.id'), nullable=False),
    Column('is_active', Boolean, nullable=False, server_default=text('true')),
    created_at_column(),
)

lessons_table = Table(
    'lessons',
    metadata,
    Column('id', BIGINT, primary_key=True),
    Column('group_id', BIGINT, ForeignKey('groups.id'), nullable=True),
    Column(
        'course_teacher_student_id',
        BIGINT,
        ForeignKey('course_teacher_students.id'),
        nullable=True,
    ),
    Column(
        'cabinet_id',
        BIGINT,
        ForeignKey('cabinets.id'),
        nullable=True,
    ),
    Column('url', String(500), nullable=True),
    Column(
        'conducted_by_id',
        BIGINT,
        ForeignKey('users.id'),
        nullable=False,
    ),
    Column('start_date', DateTime(timezone=True), nullable=False),
    Column('end_date', DateTime(timezone=True), nullable=False),
    created_at_column(),
)

attendance_table = Table(
    'attendance',
    metadata,
    Column('id', BIGINT, primary_key=True),
    Column('lesson_id', BIGINT, ForeignKey('lessons.id'), nullable=False),
    Column('user_id', BIGINT, ForeignKey('users.id'), nullable=False),
    Column('status', attendance_status_enum, nullable=False),
    Column('comment', Text, nullable=False, server_default=text("''")),
)

feedback_table = Table(
    'feedback',
    metadata,
    Column('id', BIGINT, primary_key=True),
    Column('author_id', BIGINT, ForeignKey('users.id'), nullable=False),
    Column('teacher_id', BIGINT, ForeignKey('users.id'), nullable=True),
    Column('course_id', BIGINT, ForeignKey('courses.id'), nullable=True),
    Column('rating', Integer, nullable=False),
    Column('text', Text, nullable=False, server_default=text("''")),
    Column('is_active', Boolean, nullable=False, server_default=text('true')),
    created_at_column(),
)

payments_table = Table(
    'payments',
    metadata,
    Column('id', BIGINT, primary_key=True),
    Column('group_id', BIGINT, ForeignKey('groups.id'), nullable=True),
    Column('user_id', BIGINT, ForeignKey('users.id'), nullable=True),
    Column('lesson_id', BIGINT, ForeignKey('lessons.id'), nullable=True),
    Column('amount', Integer, nullable=False),
    Column(
        'created_by_id',
        BIGINT,
        ForeignKey('users.id'),
        nullable=False,
    ),
    Column(
        'date',
        DateTime(timezone=True),
        nullable=False,
        server_default=text('NOW()'),
    ),
)

mapper_registry.map_imperatively(Organization, organizations_table)
mapper_registry.map_imperatively(User, users_table)
mapper_registry.map_imperatively(
    OrganizationMember,
    organization_members_table,
    properties={'user': relationship(User)},
)


mapper_registry.map_imperatively(Subject, subjects_table)
mapper_registry.map_imperatively(
    Course,
    courses_table,
    properties={'subject': relationship(Subject)},
)
mapper_registry.map_imperatively(
    CourseTeacher,
    course_teachers_table,
    properties={
        'course': relationship(Course),
        'teacher': relationship(User),
    },
)
mapper_registry.map_imperatively(
    CourseTeacherStudent,
    course_teacher_students_table,
    properties={
        'course_teacher': relationship(CourseTeacher),
        'student': relationship(User),
    },
)

mapper_registry.map_imperatively(
    Address,
    addresses_table,
    properties={'cabinets': relationship(Cabinet, back_populates='address')},
)
mapper_registry.map_imperatively(
    Cabinet,
    cabinets_table,
    properties={'address': relationship(Address, back_populates='cabinets')},
)

mapper_registry.map_imperatively(
    Group,
    groups_table,
    properties={
        'course': relationship(Course),
        'default_cabinet': relationship(Cabinet),
    },
)
mapper_registry.map_imperatively(UserGroup, user_groups_table)

mapper_registry.map_imperatively(
    Lesson,
    lessons_table,
    properties={
        'cabinet': relationship(Cabinet),
        'group': relationship(Group),
        'course_teacher_student': relationship(CourseTeacherStudent),
    },
)
mapper_registry.map_imperatively(Attendance, attendance_table)
mapper_registry.map_imperatively(Feedback, feedback_table)
mapper_registry.map_imperatively(Payment, payments_table)
