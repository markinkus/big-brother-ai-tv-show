"""simulation core layers

Revision ID: 20260323_0005
Revises: 20260323_0004
Create Date: 2026-03-23 23:45:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260323_0005"
down_revision = "20260323_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "contestant_states",
        sa.Column("contestant_id", sa.Integer(), sa.ForeignKey("contestants.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("room_id", sa.Integer(), sa.ForeignKey("rooms.id"), nullable=True),
        sa.Column("energy", sa.Float(), nullable=False, server_default="70"),
        sa.Column("stress", sa.Float(), nullable=False, server_default="24"),
        sa.Column("suspicion", sa.Float(), nullable=False, server_default="18"),
        sa.Column("trust_baseline", sa.Float(), nullable=False, server_default="50"),
        sa.Column("loneliness", sa.Float(), nullable=False, server_default="22"),
        sa.Column("ambition", sa.Float(), nullable=False, server_default="55"),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="52"),
        sa.Column("social_visibility", sa.Float(), nullable=False, server_default="26"),
        sa.Column("current_focus", sa.String(length=120), nullable=False, server_default="settling_in"),
        sa.Column("status_effects_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "objectives",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("contestant_id", sa.Integer(), sa.ForeignKey("contestants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("objective_type", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("priority", sa.Float(), nullable=False, server_default="50"),
        sa.Column("duration_ticks", sa.Integer(), nullable=False, server_default="24"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("success_conditions_json", sa.JSON(), nullable=False),
        sa.Column("failure_conditions_json", sa.JSON(), nullable=False),
        sa.Column("reward_json", sa.JSON(), nullable=False),
        sa.Column("penalty_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "memories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("contestant_id", sa.Integer(), sa.ForeignKey("contestants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("memory_type", sa.String(length=40), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("salience", sa.Float(), nullable=False, server_default="0"),
        sa.Column("emotional_valence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("strategic_value", sa.Float(), nullable=False, server_default="0"),
        sa.Column("related_contestant_ids_json", sa.JSON(), nullable=False),
        sa.Column("related_event_id", sa.Integer(), sa.ForeignKey("simulation_events.id"), nullable=True),
        sa.Column("decay_rate", sa.Float(), nullable=False, server_default="0.15"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "confessionals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("contestant_id", sa.Integer(), sa.ForeignKey("contestants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("triggered_by_event_id", sa.Integer(), sa.ForeignKey("simulation_events.id"), nullable=True),
        sa.Column("public_transcript", sa.Text(), nullable=False),
        sa.Column("private_analysis", sa.Text(), nullable=False),
        sa.Column("shadow_flags_json", sa.JSON(), nullable=False),
        sa.Column("contradiction_flags_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "highlights",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("season_id", sa.Integer(), sa.ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("simulation_events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("highlights")
    op.drop_table("confessionals")
    op.drop_table("memories")
    op.drop_table("objectives")
    op.drop_table("contestant_states")
