"""
Base domain entities and value objects.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.core.database import Base


class BaseEntity(Base):
    """Base entity with common fields for all domain entities."""
    
    __abstract__ = True
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


class TenantAwareEntity(BaseEntity):
    """Base entity for tenant-aware entities."""
    
    __abstract__ = True
    
    tenant_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        index=True
    )


class DomainEvent:
    """Base class for domain events."""
    
    def __init__(self, event_type: str, data: Dict[str, Any], tenant_id: Optional[str] = None):
        self.event_type = event_type
        self.data = data
        self.tenant_id = tenant_id
        self.timestamp = datetime.utcnow()
        self.event_id = str(uuid.uuid4())


class AggregateRoot(TenantAwareEntity):
    """Base class for aggregate roots with domain events."""
    
    __abstract__ = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._domain_events: List[DomainEvent] = []
    
    def add_domain_event(self, event: DomainEvent) -> None:
        """Add a domain event to the aggregate."""
        self._domain_events.append(event)
    
    def clear_domain_events(self) -> None:
        """Clear all domain events."""
        self._domain_events.clear()
    
    def get_domain_events(self) -> List[DomainEvent]:
        """Get all domain events."""
        return self._domain_events.copy()


class ValueObject:
    """Base class for value objects."""
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__
    
    def __hash__(self) -> int:
        return hash(tuple(sorted(self.__dict__.items())))


class Repository:
    """Base repository interface."""
    
    def __init__(self, session):
        self.session = session
