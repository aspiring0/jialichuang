"""
Session Management Endpoints
"""

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.session import Session, SessionStatus

router = APIRouter()


# ============================================
# Pydantic Schemas
# ============================================
class SessionCreate(BaseModel):
    """Schema for creating a new session"""

    title: Optional[str] = Field(None, max_length=255)


class SessionResponse(BaseModel):
    """Schema for session response"""

    id: uuid.UUID
    title: Optional[str]
    status: SessionStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SessionUpdate(BaseModel):
    """Schema for updating a session"""

    title: Optional[str] = Field(None, max_length=255)
    status: Optional[SessionStatus] = None


class SessionListResponse(BaseModel):
    """Schema for session list response"""

    sessions: List[SessionResponse]
    total: int


# ============================================
# Endpoints
# ============================================
@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new conversation session.
    Each session gets a unique Session_ID.
    """
    new_session = Session(
        title=session_data.title or "New Conversation",
        status=SessionStatus.ACTIVE,
    )
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)

    return new_session


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    status_filter: Optional[SessionStatus] = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """
    List all sessions with optional filtering.
    """
    query = select(Session)

    if status_filter:
        query = query.where(Session.status == status_filter)

    # Get total count
    count_query = select(Session)
    if status_filter:
        count_query = count_query.where(Session.status == status_filter)
    result = await db.execute(count_query)
    total = len(result.scalars().all())

    # Get paginated results
    query = query.order_by(Session.updated_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    sessions = result.scalars().all()

    return SessionListResponse(
        sessions=[SessionResponse.model_validate(s) for s in sessions],
        total=total,
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific session by ID.
    """
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    return session


@router.patch("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: uuid.UUID,
    update_data: SessionUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a session's title or status.
    """
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    if update_data.title is not None:
        session.title = update_data.title
    if update_data.status is not None:
        session.status = update_data.status

    await db.commit()
    await db.refresh(session)

    return session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a session (soft delete by setting status to DELETED).
    """
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    session.status = SessionStatus.DELETED
    await db.commit()

    return None