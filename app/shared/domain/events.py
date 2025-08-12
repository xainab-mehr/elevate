"""
Domain events for the application.
"""

from typing import Any, Dict

from app.shared.domain.base import DomainEvent


class UserRegisteredEvent(DomainEvent):
    """Event fired when a user registers."""
    
    def __init__(self, user_id: str, email: str, role: str, tenant_id: str):
        super().__init__(
            event_type="user.registered",
            data={
                "user_id": user_id,
                "email": email,
                "role": role,
            },
            tenant_id=tenant_id
        )


class TeamFormedEvent(DomainEvent):
    """Event fired when a team is formed."""
    
    def __init__(self, team_id: str, course_id: str, project_id: str, member_ids: list, tenant_id: str):
        super().__init__(
            event_type="team.formed",
            data={
                "team_id": team_id,
                "course_id": course_id,
                "project_id": project_id,
                "member_ids": member_ids,
            },
            tenant_id=tenant_id
        )


class QuestionnaireCompletedEvent(DomainEvent):
    """Event fired when a questionnaire is completed."""
    
    def __init__(self, questionnaire_id: str, user_id: str, course_id: str, tenant_id: str):
        super().__init__(
            event_type="questionnaire.completed",
            data={
                "questionnaire_id": questionnaire_id,
                "user_id": user_id,
                "course_id": course_id,
            },
            tenant_id=tenant_id
        )


class CourseCreatedEvent(DomainEvent):
    """Event fired when a course is created."""
    
    def __init__(self, course_id: str, instructor_id: str, course_name: str, tenant_id: str):
        super().__init__(
            event_type="course.created",
            data={
                "course_id": course_id,
                "instructor_id": instructor_id,
                "course_name": course_name,
            },
            tenant_id=tenant_id
        )
