"""create meal_items

Revision ID: 0003_create_meal_items
Revises: 0002_create_meals
Create Date: 2026-01-22
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_create_meal_items"
down_revision = "0002_create_meals"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "meal_items",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("meal_id", sa.UUID(as_uuid=True), sa.ForeignKey("meals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("quantity", sa.Numeric(8, 2), nullable=True),
        sa.Column("unit", sa.Text(), nullable=True),
        sa.Column("calories", sa.Integer(), nullable=False),
        sa.Column("protein_g", sa.Numeric(6, 2), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("calories >= 0", name="ck_meal_items_calories_nonneg"),
        sa.CheckConstraint("protein_g >= 0", name="ck_meal_items_protein_nonneg"),
        sa.UniqueConstraint("meal_id", "position", name="uq_meal_items_meal_id_position"),
    )
    op.create_index("ix_meal_items_meal_position", "meal_items", ["meal_id", "position"])


def downgrade() -> None:
    op.drop_index("ix_meal_items_meal_position", table_name="meal_items")
    op.drop_table("meal_items")
