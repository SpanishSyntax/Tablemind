"""'fix_schemas_to_jobs_and_resources'

Revision ID: 539143a3032a
Revises: 539143a3031a
Create Date: 2025-11-14 16:43:22.794616

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "539143a3032a"
down_revision: str = "539143a3031a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # --- RESOURCES: MODELS ---
    op.create_table(
        "ai_models",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("encoder", sa.String(), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=False),
        sa.Column("top_p", sa.Float(), nullable=False),
        sa.Column("endpoint_url", sa.String(), nullable=False),
        sa.Column("cost_per_1m_input", sa.Integer(), nullable=False),
        sa.Column("cost_per_1m_output", sa.Integer(), nullable=False),
        sa.Column("max_input_tokens", sa.Integer(), nullable=False),
        sa.Column("max_output_tokens", sa.Integer(), nullable=False),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        schema="resources",
    )

    # --- RESOURCES: API_KEYS ---
    op.create_table(
        "api_keys",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("model_id", sa.UUID(), nullable=False),
        sa.Column("api_key", sa.String(length=256), nullable=False),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column(
            "usage_count", sa.Integer(), nullable=False, server_default=sa.text("0")
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["model_id"], ["resources.ai_models.id"], ondelete="CASCADE"
        ),
        schema="resources",
    )
    op.create_index(
        "ix_resources_api_keys_key",
        "api_keys",
        ["api_key"],
        unique=True,
        schema="resources",
    )

    # --- RESOURCES: PROMPTS ---
    op.create_table(
        "prompts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("prompt_text", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("hash", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("hash"),
        sa.ForeignKeyConstraint(["user_id"], ["auth.users.id"], ondelete="CASCADE"),
        schema="resources",
    )
    op.create_index(
        "ix_resources_prompts_hash",
        "prompts",
        ["hash"],
        unique=True,
        schema="resources",
    )

    # --- JOBS: JOBS ---
    op.create_table(
        "jobs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("model_id", sa.UUID(), nullable=False),
        sa.Column("prompt_id", sa.UUID(), nullable=False),
        sa.Column("media_id", sa.UUID(), nullable=False),
        sa.Column(
            "job_status",
            sa.Enum(
                "QUEUED", "RUNNING", "FINISHED", "CANCELLED", "FAILED", name="jobstatus"
            ),
            nullable=False,
        ),
        sa.Column("cost_estimate_usd", sa.Integer(), nullable=False),
        sa.Column("input_token_count", sa.Integer(), nullable=False),
        sa.Column("output_token_count", sa.Integer(), nullable=False),
        sa.Column(
            "combined_results", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("hash", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("hash"),
        sa.ForeignKeyConstraint(["model_id"], ["resources.ai_models.id"]),
        sa.ForeignKeyConstraint(["prompt_id"], ["resources.prompts.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["auth.users.id"]),
        schema="jobs",
    )
    op.create_index("ix_jobs_jobs_hash", "jobs", ["hash"], unique=True, schema="jobs")

    # --- JOBS: CHUNKS ---
    op.create_table(
        "chunks",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("job_id", sa.UUID(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("total_rows", sa.Integer(), nullable=False),
        sa.Column("row_range", sa.String(), nullable=False),
        sa.Column(
            "granularity",
            sa.Enum("PER_ROW", "PER_CELL", name="granularitylevel"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "QUEUED", "RUNNING", "FINISHED", "CANCELLED", "FAILED", name="jobstatus"
            ),
            nullable=False,
        ),
        sa.Column(
            "source_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column(
            "output_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("hash", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("hash"),
        sa.ForeignKeyConstraint(["user_id"], ["auth.users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.jobs.id"], ondelete="CASCADE"),
        schema="jobs",
    )
    op.create_index(
        "ix_jobs_chunks_hash", "chunks", ["hash"], unique=True, schema="jobs"
    )


def downgrade() -> None:
    op.drop_table("chunks", schema="jobs")
    op.drop_table("jobs", schema="jobs")
    op.drop_table("api_keys", schema="resources")
    op.drop_table("ai_models", schema="resources")
    op.drop_table("prompts", schema="resources")
