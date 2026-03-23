"""character skin fields

Revision ID: 20260323_0004
Revises: 20260323_0003
Create Date: 2026-03-23 23:10:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260323_0004"
down_revision = "20260323_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("contestants", sa.Column("skin_palette", sa.String(length=40), nullable=False, server_default="studio_blue"))
    op.add_column("contestants", sa.Column("skin_accent", sa.String(length=40), nullable=False, server_default="gold"))
    op.add_column("contestants", sa.Column("skin_silhouette", sa.String(length=40), nullable=False, server_default="host-ready"))
    op.add_column("contestants", sa.Column("hair_style", sa.String(length=40), nullable=False, server_default="crown"))


def downgrade() -> None:
    op.drop_column("contestants", "hair_style")
    op.drop_column("contestants", "skin_silhouette")
    op.drop_column("contestants", "skin_accent")
    op.drop_column("contestants", "skin_palette")
