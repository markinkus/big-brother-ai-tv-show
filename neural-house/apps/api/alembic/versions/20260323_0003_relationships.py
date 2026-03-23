"""relationships

Revision ID: 20260323_0003
Revises: 20260323_0002
Create Date: 2026-03-23 20:55:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260323_0003"
down_revision = "20260323_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "relationships",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("season_id", sa.Integer(), sa.ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_contestant_id", sa.Integer(), sa.ForeignKey("contestants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_contestant_id", sa.Integer(), sa.ForeignKey("contestants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("trust", sa.Float(), nullable=False, server_default="50"),
        sa.Column("attraction", sa.Float(), nullable=False, server_default="15"),
        sa.Column("rivalry", sa.Float(), nullable=False, server_default="18"),
        sa.Column("fear", sa.Float(), nullable=False, server_default="10"),
        sa.Column("respect", sa.Float(), nullable=False, server_default="40"),
        sa.Column("manipulation", sa.Float(), nullable=False, server_default="12"),
        sa.Column("familiarity", sa.Float(), nullable=False, server_default="20"),
        sa.Column("last_significant_change_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_relationships_unique_pair",
        "relationships",
        ["season_id", "source_contestant_id", "target_contestant_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_relationships_unique_pair", table_name="relationships")
    op.drop_table("relationships")
