import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List

from shared_db import Base
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.targets import TargetTable

if TYPE_CHECKING:
    from models import Job_on_db

MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB


class MediaType(str, Enum):
    IMAGE_PNG = "image/png"
    IMAGE_JPEG = "image/jpeg"
    VIDEO_MP4 = "video/mp4"
    TABLE_EXCEL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    TABLE_OPEN = "application/vnd.oasis.opendocument.spreadsheet"
    TABLE_CSV = "text/csv"
    TABLE_TSV = "text/tab-separated-values"


class Prompt_on_db(Base):
    __tablename__ = TargetTable.PROMPTS.table
    __table_args__ = {"schema": TargetTable.PROMPTS.schema}

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{TargetTable.USERS.fq_name}.id"))

    prompt_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    hash: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )

    jobs: Mapped[List["Job_on_db"]] = relationship(
        "Job_on_db", back_populates="prompt", cascade="all, delete-orphan"
    )


class Model_on_db(Base):
    __tablename__ = TargetTable.MODELS.table
    __table_args__ = {"schema": TargetTable.MODELS.schema}

    name: Mapped[str] = mapped_column(
        nullable=False, unique=True
    )  # e.g., gpt-4, deepseek-chat, llama3
    provider: Mapped[str] = mapped_column(nullable=False)  # openai, deepseek, local
    encoder: Mapped[str] = mapped_column(nullable=False)  # openai, deepseek, local

    temperature: Mapped[float] = mapped_column(nullable=False)
    top_p: Mapped[float] = mapped_column(nullable=False)
    endpoint_url: Mapped[str] = mapped_column(nullable=False)

    cost_per_1m_input: Mapped[int] = mapped_column(nullable=False)
    cost_per_1m_output: Mapped[int] = mapped_column(nullable=False)

    max_input_tokens: Mapped[int] = mapped_column(nullable=False)
    max_output_tokens: Mapped[int] = mapped_column(nullable=False)

    is_active: Mapped[bool] = mapped_column(nullable=False, default=False)

    jobs: Mapped[List["Job_on_db"]] = relationship(
        "Job_on_db", back_populates="model", cascade="all, delete-orphan"
    )
    api_keys: Mapped[List["APIKey_on_db"]] = relationship(
        "APIKey_on_db", back_populates="model"
    )


class APIKey_on_db(Base):
    __tablename__ = TargetTable.API_KEYS.table
    __table_args__ = {"schema": TargetTable.API_KEYS.schema}

    model_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{TargetTable.MODELS.fq_name}.id"))
    api_key: Mapped[str] = mapped_column(
        String(256), nullable=False, unique=True, index=True
    )
    is_active: Mapped[bool] = mapped_column(nullable=False, default=False)
    usage_count: Mapped[int] = mapped_column(nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used: Mapped[datetime] = mapped_column(nullable=True)

    model: Mapped["Model_on_db"] = relationship(
        "Model_on_db", back_populates="api_keys"
    )
