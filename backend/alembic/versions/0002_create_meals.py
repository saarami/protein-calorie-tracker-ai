"""create meals

Revision ID: 0002_create_meals
Revises: 0001_create_users
Create Date: 2026-01-22
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_create_meals"
down_revision = "0001_create_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "meals",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("total_calories", sa.Integer(), nullable=False),
        sa.Column("total_protein_g", sa.Numeric(6, 2), nullable=False),
        sa.Column("meal_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("total_calories >= 0", name="ck_meals_total_calories_nonneg"),
        sa.CheckConstraint("total_protein_g >= 0", name="ck_meals_total_protein_nonneg"),
    )
    op.create_index("ix_meals_user_date", "meals", ["user_id", "meal_date"])
    op.create_index("ix_meals_user_created_at", "meals", ["user_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_meals_user_created_at", table_name="meals")
    op.drop_index("ix_meals_user_date", table_name="meals")
    op.drop_table("meals")
