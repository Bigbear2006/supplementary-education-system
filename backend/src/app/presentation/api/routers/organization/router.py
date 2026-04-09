from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from fastapi.params import Depends

from app.application.use_cases.organization.create import (
    CreateOrganization,
    CreateOrganizationDTO,
)
from app.application.use_cases.organization.get_all import GetAllOrganizations
from app.application.use_cases.organization.get_current import (
    GetCurrentOrganization,
)
from app.application.use_cases.organization.get_current_org_all_members import (
    GetCurrentOrganizationAllMembers,
)
from app.application.use_cases.organization.get_current_org_member import (
    GetCurrentOrganizationMember,
)
from app.application.use_cases.organization.get_my import GetMyOrganizations
from app.application.use_cases.organization.join import JoinOrganization
from app.application.use_cases.organization.update_member import (
    UpdateOrganizationMember,
    UpdateOrganizationMemberDTO,
)
from app.presentation.api.common.cookie import cookie_scheme
from app.presentation.api.routers.organization.models import (
    MyOrganizationResponse,
    OrganizationMemberDetailResponse,
    OrganizationMemberResponse,
    OrganizationResponse,
    UpdateOrganizationMemberRequest,
)

organization_router = APIRouter(
    prefix='/organizations',
    route_class=DishkaRoute,
    tags=['organizations'],
)


@organization_router.post(
    '/',
    status_code=201,
    dependencies=[Depends(cookie_scheme)],
)
async def create_organization_router(
    data: CreateOrganizationDTO,
    create_organization: FromDishka[CreateOrganization],
) -> OrganizationResponse:
    org = await create_organization(data)
    return OrganizationResponse.model_validate(org)


@organization_router.get('/')
async def get_organizations_router(
    get_all_organizations: FromDishka[GetAllOrganizations],
) -> list[OrganizationResponse]:
    orgs = await get_all_organizations()
    return [OrganizationResponse.model_validate(org) for org in orgs]


@organization_router.get('/current/')
async def get_current_organization_router(
    get_current_organization: FromDishka[GetCurrentOrganization],
) -> OrganizationResponse:
    org = await get_current_organization()
    return OrganizationResponse.model_validate(org)


@organization_router.get('/my/', dependencies=[Depends(cookie_scheme)])
async def get_my_organizations_router(
    get_my_organizations: FromDishka[GetMyOrganizations],
) -> list[MyOrganizationResponse]:
    orgs = await get_my_organizations()
    return [MyOrganizationResponse.model_validate(org) for org in orgs]


@organization_router.post('/current/members/', status_code=201)
async def join_organization_router(
    join_organization: FromDishka[JoinOrganization],
) -> OrganizationMemberResponse:
    member = await join_organization()
    return OrganizationMemberResponse.model_validate(member)


@organization_router.get('/current/members/')
async def get_current_organization_members_router(
    get_all_organization_members: FromDishka[GetCurrentOrganizationAllMembers],
) -> list[OrganizationMemberDetailResponse]:
    members = await get_all_organization_members()
    return [
        OrganizationMemberDetailResponse.model_validate(member)
        for member in members
    ]


@organization_router.get('/current/members/me/')
async def get_current_organization_member_router(
    get_organization_member: FromDishka[GetCurrentOrganizationMember],
) -> OrganizationMemberResponse:
    member = await get_organization_member()
    return OrganizationMemberResponse.model_validate(member)


@organization_router.patch('/current/members/{user_id}/')
async def update_organization_member_router(
    user_id: int,
    data: UpdateOrganizationMemberRequest,
    update_org_member: FromDishka[UpdateOrganizationMember],
) -> OrganizationMemberResponse:
    dto = UpdateOrganizationMemberDTO(user_id, data.role)
    member = await update_org_member(dto)
    return OrganizationMemberResponse.model_validate(member)
