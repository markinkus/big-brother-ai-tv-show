"""initial foundation

Revision ID: 20260323_0001
Revises:
Create Date: 2026-03-23 10:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260323_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "seasons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="draft"),
        sa.Column("seed", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "premium_users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("premium_tier", sa.String(length=50), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "rooms",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("season_id", sa.Integer(), sa.ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("x", sa.Integer(), nullable=False),
        sa.Column("y", sa.Integer(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
    )
    op.create_table(
        "contestants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("season_id", sa.Integer(), sa.ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("archetype", sa.String(length=80), nullable=False),
        sa.Column("avatar_seed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("public_bio", sa.Text(), nullable=False),
        sa.Column("public_goal", sa.Text(), nullable=False),
        sa.Column("hidden_goal_summary", sa.Text(), nullable=False),
        sa.Column("speech_style", sa.String(length=120), nullable=False),
        sa.Column("persona_card_id", sa.Integer(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "persona_cards",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("season_id", sa.Integer(), sa.ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("label", sa.String(length=160), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("base_seed", sa.Integer(), nullable=False),
        sa.Column("dominant_archetype", sa.String(length=80), nullable=False),
        sa.Column("synopsis", sa.Text(), nullable=False),
        sa.Column("public_pitch", sa.Text(), nullable=False),
        sa.Column("private_complexity_summary", sa.Text(), nullable=False),
        sa.Column("trustability_score", sa.Float(), nullable=False),
        sa.Column("manipulation_susceptibility", sa.Float(), nullable=False),
        sa.Column("generation_notes_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "journalists",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("season_id", sa.Integer(), sa.ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("style", sa.String(length=80), nullable=False),
        sa.Column("ideology", sa.String(length=120), nullable=False),
        sa.Column("sensationalism", sa.Float(), nullable=False),
        sa.Column("empathy", sa.Float(), nullable=False),
        sa.Column("bias_profile_json", sa.JSON(), nullable=False),
        sa.Column("activity_interval_ticks", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_table(
        "simulation_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("season_id", sa.Integer(), sa.ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tick_number", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("room_id", sa.Integer(), sa.ForeignKey("rooms.id"), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("tension_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "articles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("season_id", sa.Integer(), sa.ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("journalist_id", sa.Integer(), sa.ForeignKey("journalists.id"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("dek", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("tone", sa.String(length=80), nullable=False),
        sa.Column("stance", sa.String(length=80), nullable=False),
        sa.Column("referenced_event_ids_json", sa.JSON(), nullable=False),
        sa.Column("referenced_contestant_ids_json", sa.JSON(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("visibility_scope", sa.String(length=50), nullable=False),
    )
    op.create_table(
        "vip_access_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("premium_user_id", sa.Integer(), sa.ForeignKey("premium_users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("season_id", sa.Integer(), sa.ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("selected_room_code", sa.String(length=80), nullable=True),
        sa.Column("session_meta_json", sa.JSON(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("vip_access_sessions")
    op.drop_table("articles")
    op.drop_table("simulation_events")
    op.drop_table("journalists")
    op.drop_table("persona_cards")
    op.drop_table("contestants")
    op.drop_table("rooms")
    op.drop_table("premium_users")
    op.drop_table("seasons")

