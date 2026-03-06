"""
Task Model - Analysis tasks in the blackboard system
"""

import enum
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import DateTime, Enum, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TaskStatus(enum.Enum):
    """Task status enum"""

    PENDING = "pending"
    CLAIMED = "claimed"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class TaskType(enum.Enum):
    """Task type enum"""

    DATA_PARSING = "data_parsing"
    ANALYSIS = "analysis"
    VISUALIZATION = "visualization"
    DEBUGGING = "debugging"


class Task(Base):
    """Analysis task model for the blackboard system"""

    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Reference to the session this task belongs to",
    )
    type: Mapped[TaskType] = mapped_column(
        Enum(TaskType),
        nullable=False,
        index=True,
    )
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus),
        default=TaskStatus.PENDING,
        index=True,
    )
    priority: Mapped[int] = mapped_column(
        Integer,
        default=5,
        comment="Priority from 1 (highest) to 10 (lowest)",
    )
    tags: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Tags for task routing (e.g., ['csv_read', 'pandas'])",
    )
    dependencies: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="List of parent task UUIDs this task depends on",
    )
    input_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Input data for the task (file_path, user_query, etc.)",
    )
    output_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Output/result from the task execution",
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Error message if task failed",
    )
    claimed_by: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Agent ID that claimed this task",
    )
    timeout_seconds: Mapped[int] = mapped_column(
        Integer,
        default=300,
        comment="Task timeout in seconds",
    )
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    max_retries: Mapped[int] = mapped_column(
        Integer,
        default=3,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<Task {self.id} ({self.type.value})>"