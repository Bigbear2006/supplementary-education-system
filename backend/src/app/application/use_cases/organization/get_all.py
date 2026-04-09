from app.application.repositories.organization import OrganizationRepository
from app.domain.entities import Organization


class GetAllOrganizations:
    def __init__(
        self,
        organization_repository: OrganizationRepository,
    ) -> None:
        self.organization_repository = organization_repository

    async def __call__(self) -> list[Organization]:
        return await self.organization_repository.get_all()
