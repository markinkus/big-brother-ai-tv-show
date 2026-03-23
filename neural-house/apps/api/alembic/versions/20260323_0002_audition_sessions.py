"""audition sessions

Revision ID: 20260323_0002
Revises: 20260323_0001
Create Date: 2026-03-23 21:10:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260323_0002"
down_revision = "20260323_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audition_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("environment_code", sa.String(length=80), nullable=False),
        sa.Column("environment_label", sa.String(length=120), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("api_base_url", sa.String(length=255), nullable=True),
        sa.Column("model_name", sa.String(length=160), nullable=False),
        sa.Column("provider_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("character_name", sa.String(length=120), nullable=False),
        sa.Column("archetype", sa.String(length=80), nullable=False),
        sa.Column("speech_style", sa.String(length=160), nullable=False),
        sa.Column("public_hook", sa.Text(), nullable=False),
        sa.Column("traits_json", sa.JSON(), nullable=False),
        sa.Column("strengths_json", sa.JSON(), nullable=False),
        sa.Column("weaknesses_json", sa.JSON(), nullable=False),
        sa.Column("skin_palette", sa.String(length=40), nullable=False),
        sa.Column("skin_accent", sa.String(length=40), nullable=False),
        sa.Column("skin_silhouette", sa.String(length=40), nullable=False),
        sa.Column("hair_style", sa.String(length=40), nullable=False, server_default="crown"),
        sa.Column("simulated_minutes", sa.Integer(), nullable=False),
        sa.Column("playback_ms_per_beat", sa.Integer(), nullable=False),
        sa.Column("total_beats", sa.Integer(), nullable=False),
        sa.Column("current_beat", sa.Integer(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("session_seed", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "audition_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("audition_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tick_number", sa.Integer(), nullable=False),
        sa.Column("simulated_second", sa.Integer(), nullable=False),
        sa.Column("zone", sa.String(length=80), nullable=False),
        sa.Column("action_type", sa.String(length=80), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("dialogue", sa.Text(), nullable=True),
        sa.Column("state_snapshot_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("audition_events")
    op.drop_table("audition_sessions")
