import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from shared_db import Base
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy import Enum as PgEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.targets import TargetTable

if TYPE_CHECKING:
    from models import Model_on_db, Prompt_on_db


class JobStatus(str, Enum):
    QUEUED = "en cola"
    RUNNING = "corriendo"
    FINISHED = "finalizado"
    CANCELLED = "cancelado"
    FAILED = "fallido"


class GranularityLevel(str, Enum):
    PER_ROW = "Per row"
    PER_CELL = "Per cell"

    def __str__(self):
        return self.name  # Now FastAPI uses the key for parsing


class Job_on_db(Base):
    __tablename__ = TargetTable.JOBS.table
    __table_args__ = {"schema": TargetTable.JOBS.schema}

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f"{TargetTable.USERS.fq_name}.id"), nullable=False
    )
    model_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f"{TargetTable.MODELS.fq_name}.id"), nullable=False
    )
    prompt_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f"{TargetTable.PROMPTS.fq_name}.id"), nullable=False
    )
    media_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f"{TargetTable.FILES.fq_name}.id"), nullable=False
    )

    job_status: Mapped[JobStatus] = mapped_column(PgEnum(JobStatus), nullable=False)
    cost_estimate_usd: Mapped[int] = mapped_column(nullable=False)
    input_token_count: Mapped[int] = mapped_column(nullable=False)
    output_token_count: Mapped[int] = mapped_column(nullable=False)
    combined_results: Mapped[Optional[List[dict]]] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    hash: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )

    prompt: Mapped["Prompt_on_db"] = relationship("Prompt_on_db", back_populates="jobs")
    model: Mapped["Model_on_db"] = relationship("Model_on_db", back_populates="jobs")


class Chunk_on_db(Base):
    __tablename__ = TargetTable.CHUNKS.table
    __table_args__ = {"schema": TargetTable.CHUNKS.schema}

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f"{TargetTable.USERS.fq_name}.id"), nullable=False
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f"{TargetTable.JOBS.fq_name}.id"), nullable=False
    )

    chunk_index: Mapped[int] = mapped_column(nullable=False)
    total_rows: Mapped[int] = mapped_column(nullable=False)
    row_range: Mapped[str] = mapped_column(nullable=False)  # e.g. "10-19"

    granularity: Mapped[GranularityLevel] = mapped_column(
        PgEnum(GranularityLevel), nullable=False
    )
    status: Mapped[JobStatus] = mapped_column(PgEnum(JobStatus), nullable=False)

    source_data: Mapped[List[dict]] = mapped_column(JSONB, nullable=False)
    output_data: Mapped[Optional[List[dict]]] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        onupdate=func.now(), nullable=True
    )

    hash: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )
