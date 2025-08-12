"""
Users domain repository interfaces.
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from app.users.domain.entities import User


class UserRepositoryInterface(ABC):
    """User repository interface."""
    
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def get_by_id_and_tenant(self, user_id: str, tenant_id: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str, tenant_id: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def create(self, user: User) -> User:
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        pass
    
    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        pass
    
    @abstractmethod
    async def list_by_tenant(self, tenant_id: str, skip: int = 0, limit: int = 100) -> List[User]:
        pass
