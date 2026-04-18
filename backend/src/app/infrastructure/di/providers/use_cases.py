from dishka import Provider, Scope, provide_all

from app.application.use_cases.address import (
    CreateAddress,
    DeleteAddress,
    GetAllAddresses,
    UpdateAddress,
)
from app.application.use_cases.cabinet import CreateCabinet, DeleteCabinet
from app.application.use_cases.course import (
    AddCurrentStudentToCourse,
    AddTeacherToCourse,
    CreateCourse,
    DeleteTeacherFromCourse,
    GetAllCourses,
    GetCourseTeachers,
    GetCourseTeacherStudents,
    GetMyCourses,
    UpdateCourse,
)
from app.application.use_cases.group import (
    AddUserToGroup,
    CreateGroup,
    GetAllGroups,
    GetGroupById,
    GetGroupUsers,
    RemoveUserFromGroup,
    UpdateGroup,
)
from app.application.use_cases.lesson import CreateLesson, GetMyLessons
from app.application.use_cases.organization import (
    CreateOrganization,
    GetAllOrganizations,
    GetCurrentOrganization,
    GetCurrentOrganizationAllMembers,
    GetCurrentOrganizationMember,
    GetMyOrganizations,
    JoinOrganization,
    UpdateOrganizationMember,
)
from app.application.use_cases.subject import (
    CreateSubject,
    DeleteSubject,
    GetAllSubjects,
    UpdateSubject,
)
from app.application.use_cases.user import (
    ChangeUserPassword,
    GetCurrentUser,
    LoginUser,
    RegisterUser,
    UpdateCurrentUser,
)


class UseCasesProvider(Provider):
    scope = Scope.REQUEST

    user = provide_all(
        RegisterUser,
        LoginUser,
        GetCurrentUser,
        UpdateCurrentUser,
        ChangeUserPassword,
    )
    organization = provide_all(
        CreateOrganization,
        JoinOrganization,
        GetAllOrganizations,
        GetCurrentOrganization,
        GetCurrentOrganizationMember,
        GetMyOrganizations,
        GetCurrentOrganizationAllMembers,
        UpdateOrganizationMember,
    )
    address = provide_all(
        CreateAddress,
        GetAllAddresses,
        UpdateAddress,
        DeleteAddress,
    )
    cabinet = provide_all(CreateCabinet, DeleteCabinet)
    subject = provide_all(
        CreateSubject,
        GetAllSubjects,
        UpdateSubject,
        DeleteSubject,
    )
    course = provide_all(
        CreateCourse,
        AddTeacherToCourse,
        AddCurrentStudentToCourse,
        DeleteTeacherFromCourse,
        GetAllCourses,
        GetMyCourses,
        UpdateCourse,
        GetCourseTeacherStudents,
        GetCourseTeachers,
    )
    group = provide_all(
        CreateGroup,
        GetAllGroups,
        GetGroupById,
        UpdateGroup,
        GetGroupUsers,
        AddUserToGroup,
        RemoveUserFromGroup,
    )
    lesson = provide_all(CreateLesson, GetMyLessons)
