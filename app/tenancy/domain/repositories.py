# Tenancy domain repository interfaces
from abc import ABC, abstractmethod
from typing import Optional, List

from app.tenancy.domain.entities import Organization, OrganizationSettings


class OrganizationRepositoryInterface(ABC):
    """Organization repository interface."""
    
    @abstractmethod
    async def get_by_id(self, organization_id: str) -> Optional[Organization]:
        pass
    
    @abstractmethod
    async def get_by_slug(self, slug: str) -> Optional[Organization]:
        pass
    
    @abstractmethod
    async def get_by_domain(self, domain: str) -> Optional[Organization]:
        pass
    
    @abstractmethod
    async def create(self, organization: Organization) -> Organization:
        pass
    
    @abstractmethod
    async def update(self, organization: Organization) -> Organization:
        pass
    
    @abstractmethod
    async def delete(self, organization_id: str) -> bool:
        pass
    
    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Organization]:
        pass
