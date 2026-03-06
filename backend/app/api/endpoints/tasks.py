"""
Task Management Endpoints
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.task import Task, TaskStatus, TaskType

router = APIRouter()


# ============================================
# Pydantic Schemas
# ============================================
class TaskCreate(BaseModel):
    """Schema for creating a new task"""

    session_id: uuid.UUID
    type: TaskType
    priority: int = Field(default=5, ge=1, le=10)
    tags: Optional[List[str]] = None
    dependencies: Optional[List[uuid.UUID]] = None
    input_data: Optional[Dict[str, Any]] = None
    timeout_seconds: int = Field(default=300, ge=10, le=3600)


class TaskResponse(BaseModel):
    """Schema for task response"""

    id: uuid.UUID
    session_id: uuid.UUID
    type: TaskType
    status: TaskStatus
    priority: int
    tags: Optional[Dict[str, Any]]
    dependencies: Optional[Dict[str, Any]]
    input_data: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    claimed_by: Optional[str]
    retry_count: int
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class TaskUpdate(BaseModel):
    """Schema for updating a task"""

    status: Optional[TaskStatus] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    claimed_by: Optional[str] = None


class TaskListResponse(BaseModel):
    """Schema for task list response"""

    tasks: List[TaskResponse]
    total: int


# ============================================
# Endpoints
# ============================================
@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new analysis task.
    Tasks are processed by the blackboard system.
    """
    new_task = Task(
        session_id=task_data.session_id,
        type=task_data.type,
        status=TaskStatus.PENDING,
        priority=task_data.priority,
        tags={"tags": task_data.tags} if task_data.tags else None,
        dependencies={"deps": [str(d) for d in task_data.dependencies]}
        if task_data.dependencies
        else None,
        input_data=task_data.input_data,
        timeout_seconds=task_data.timeout_seconds,
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    return new_task


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    session_id: Optional[uuid.UUID] = None,
    status_filter: Optional[TaskStatus] = None,
    type_filter: Optional[TaskType] = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """
    List tasks with optional filtering.
    """
    query = select(Task)

    if session_id:
        query = query.where(Task.session_id == session_id)
    if status_filter:
        query = query.where(Task.status == status_filter)
    if type_filter:
        query = query.where(Task.type == type_filter)

    # Get total count
    count_query = select(Task)
    if session_id:
        count_query = count_query.where(Task.session_id == session_id)
    if status_filter:
        count_query = count_query.where(Task.status == status_filter)
    if type_filter:
        count_query = count_query.where(Task.type == type_filter)
    result = await db.execute(count_query)
    total = len(result.scalars().all())

    # Get paginated results
    query = query.order_by(Task.priority.asc(), Task.created_at.asc())
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    tasks = result.scalars().all()

    return TaskListResponse(
        tasks=[TaskResponse.model_validate(t) for t in tasks],
        total=total,
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific task by ID.
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    update_data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a task's status, output, or error message.
    Used by agents to report progress.
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    if update_data.status is not None:
        task.status = update_data.status
        if update_data.status == TaskStatus.RUNNING:
            task.started_at = datetime.utcnow()
        elif update_data.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            task.completed_at = datetime.utcnow()

    if update_data.output_data is not None:
        task.output_data = update_data.output_data

    if update_data.error_message is not None:
        task.error_message = update_data.error_message

    if update_data.claimed_by is not None:
        task.claimed_by = update_data.claimed_by

    await db.commit()
    await db.refresh(task)

    return task


@router.post("/{task_id}/retry", response_model=TaskResponse)
async def retry_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Retry a failed task.
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    if task.retry_count >= task.max_retries:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task has reached max retries ({task.max_retries})",
        )

    task.retry_count += 1
    task.status = TaskStatus.PENDING
    task.claimed_by = None
    task.error_message = None
    task.started_at = None
    task.completed_at = None

    await db.commit()
    await db.refresh(task)

    return task