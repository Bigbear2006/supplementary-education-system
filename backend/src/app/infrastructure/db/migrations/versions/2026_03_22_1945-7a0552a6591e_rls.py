"""RLS

Revision ID: 7a0552a6591e
Revises: 22c75be5848e
Create Date: 2026-03-22 19:45:37.621461

"""

from collections.abc import Sequence

from alembic import op, context
from app.infrastructure.db.config import DatabaseConfig

# revision identifiers, used by Alembic.
revision: str = '7a0552a6591e'
down_revision: str | Sequence[str] | None = '22c75be5848e'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

section = context.config.config_ini_section
DB_NAME = context.config.get_section_option(section, 'DB_NAME')
APP_USER = context.config.get_section_option(section, 'APP_USER')
APP_PASSWORD = context.config.get_section_option(section, 'APP_PASSWORD')

TABLES = [
    'organizations',
    'users',
    'organization_members',
    'courses',
    'course_teachers',
    'course_teacher_students',
    'addresses',
    'cabinets',
    'groups',
    'user_groups',
    'lessons',
    'attendance',
    'feedback',
    'payments',
]

# USING / WITH CHECK expression per table
POLICY_EXPR = {
    # 'organizations': "id = current_setting('app.current_org_id')::bigint",
    # 'users': 'true',
    # 'organization_members': (
    #     "organization_id = current_setting('app.current_org_id')::bigint"
    # ),
    'subjects': (
        "organization_id = current_setting('app.current_org_id')::bigint"
    ),
    'courses': (
        'EXISTS ('
        'SELECT 1 FROM subjects '
        'WHERE subjects.id = courses.subject_id '
        "AND subjects.organization_id = current_setting('app.current_org_id')::bigint)"
    ),
    'course_teachers': (
        'EXISTS ('
        'SELECT 1 FROM courses '
        'JOIN subjects ON subjects.id = courses.subject_id '
        'WHERE subjects.id = courses.subject_id '
        "AND subjects.organization_id = current_setting('app.current_org_id')::bigint"
        ")"
    ),
    'course_teacher_students': (
        'EXISTS ('
        'SELECT 1 FROM course_teachers '
        'JOIN courses ON courses.id = course_teachers.course_id '
        'JOIN subjects ON subjects.id = courses.subject_id '
        'WHERE course_teachers.id = course_teacher_students.course_teacher_id '
        "AND subjects.organization_id = current_setting('app.current_org_id')::bigint"
        ')'
    ),
    'addresses': (
        "organization_id = current_setting('app.current_org_id')::bigint"
    ),
    'cabinets': (
        'EXISTS ('
        'SELECT 1 FROM addresses '
        'WHERE addresses.id = cabinets.address_id '
        "AND addresses.organization_id = current_setting('app.current_org_id')::bigint)"
    ),
    'groups': (
        'EXISTS ('
        'SELECT 1 FROM courses '
        'JOIN subjects ON subjects.id = courses.subject_id '
        'WHERE courses.id = groups.course_id '
        "AND subjects.organization_id = current_setting('app.current_org_id')::bigint"
        ')'
    ),
    'user_groups': (
        'EXISTS ('
        'SELECT 1 FROM groups '
        'JOIN courses ON courses.id = groups.course_id '
        'JOIN subjects ON subjects.id = courses.subject_id '
        'WHERE groups.id = user_groups.group_id '
        "AND subjects.organization_id = current_setting('app.current_org_id')::bigint"
        ')'
    ),
    'lessons': (
        'EXISTS ('
        '    SELECT 1 FROM groups '
        '    JOIN courses ON courses.id = groups.course_id '
        '    JOIN subjects ON subjects.id = courses.subject_id '
        '    WHERE groups.id = lessons.group_id '
        "    AND subjects.organization_id = current_setting('app.current_org_id')::bigint"
        ') OR EXISTS ('
        '    SELECT 1 FROM course_teacher_students cts '
        '    JOIN course_teachers ct ON ct.id = cts.course_teacher_id '
        '    JOIN courses ON courses.id = ct.course_id '
        '    JOIN subjects ON subjects.id = courses.subject_id '
        '    WHERE cts.id = lessons.course_teacher_student_id '
        "    AND subjects.organization_id = current_setting('app.current_org_id')::bigint"
        ')'
    ),
    'attendance': (
        'EXISTS ('
        '    SELECT 1 FROM lessons '
        '    JOIN groups ON groups.id = lessons.group_id '
        '    JOIN courses ON courses.id = groups.course_id '
        '    JOIN subjects ON subjects.id = courses.subject_id '
        '    WHERE lessons.id = attendance.lesson_id '
        "    AND subjects.organization_id = current_setting('app.current_org_id')::bigint"
        ')'
    ),
    'feedback': (
        'EXISTS ('
        '    SELECT 1 FROM courses '
        '    JOIN subjects ON subjects.id = courses.subject_id '
        '    WHERE courses.id = feedback.course_id '
        "    AND subjects.organization_id = current_setting('app.current_org_id')::bigint"
        ')'
    ),
    'payments': (
        'EXISTS ('
        '    SELECT 1 FROM lessons '
        '    JOIN groups ON groups.id = lessons.group_id '
        '    JOIN courses ON courses.id = groups.course_id '
        '    JOIN subjects ON subjects.id = courses.subject_id '
        '    WHERE lessons.id = payments.lesson_id '
        "    AND subjects.organization_id = current_setting('app.current_org_id')::bigint"
        ')'
    ),
}


def upgrade() -> None:
    op.execute(
        'DO $$ BEGIN '
        f"IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{APP_USER}') THEN "
        f"CREATE USER {APP_USER} WITH PASSWORD '{APP_PASSWORD}'; "
        'END IF; '
        'END $$',
    )

    op.execute(f'GRANT CONNECT ON DATABASE {DB_NAME} TO {APP_USER}')
    op.execute(f'GRANT USAGE ON SCHEMA public TO {APP_USER}')
    op.execute(
        f'GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {APP_USER}',
    )
    op.execute(
        f"GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {APP_USER}"
    )

    for table in TABLES:
        expr = POLICY_EXPR.get(table)
        if not expr:
            continue

        op.execute(f'ALTER TABLE {table} ENABLE ROW LEVEL SECURITY')
        op.execute(
            f'CREATE POLICY {table}_{APP_USER}_policy ON {table} '
            f'AS PERMISSIVE FOR ALL TO {APP_USER} '
            f'USING ({expr}) WITH CHECK ({expr})',
        )


def downgrade() -> None:
    for table in reversed(TABLES):
        op.execute(
            f'DROP POLICY IF EXISTS {table}_{APP_USER}_policy ON {table}',
        )
        op.execute(f'ALTER TABLE {table} DISABLE ROW LEVEL SECURITY')
        op.execute(
            f'REVOKE SELECT, INSERT, UPDATE, DELETE ON {table} FROM {APP_USER}',
        )

    op.execute(
        f'REVOKE SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public FROM {APP_USER}',
    )
    op.execute(
        f"REVOKE USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public FROM {APP_USER}"
    )
    op.execute(f'REVOKE USAGE ON SCHEMA public FROM {APP_USER}')
    op.execute(f'REVOKE CONNECT ON DATABASE {DB_NAME} FROM {APP_USER}')
    op.execute(f'DROP USER IF EXISTS {APP_USER}')
