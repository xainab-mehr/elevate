"""
Users infrastructure repositories.
"""

from typing import Optional, List

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.domain.base import Repository
from app.users.domain.entities import User
from app.users.domain.repositories import UserRepositoryInterface


class UserRepository(Repository, UserRepositoryInterface):
    """SQLAlchemy implementation of user repository."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session)
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id_and_tenant(self, user_id: str, tenant_id: str) -> Optional[User]:
        """Get user by ID and tenant."""
        result = await self.session.execute(
            select(User).where(
                and_(User.id == user_id, User.tenant_id == tenant_id)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str, tenant_id: str) -> Optional[User]:
        """Get user by email within tenant."""
        result = await self.session.execute(
            select(User).where(
                and_(User.email == email, User.tenant_id == tenant_id)
            )
        )
        return result.scalar_one_or_none()
    
    async def create(self, user: User) -> User:
        """Create a new user."""
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def update(self, user: User) -> User:
        """Update an existing user."""
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def delete(self, user_id: str) -> bool:
        """Delete a user."""
        user = await self.get_by_id(user_id)
        if user:
            await self.session.delete(user)
            await self.session.commit()
            return True
        return False
    
    async def list_by_tenant(self, tenant_id: str, skip: int = 0, limit: int = 100) -> List[User]:
        """List users within a tenant."""
        result = await self.session.execute(
            select(User)
            .where(User.tenant_id == tenant_id)
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        return result.scalars().all()
