"""create users

Revision ID: 0001_create_users
Revises: 
Create Date: 2026-01-22
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_create_users"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable gen_random_uuid()
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    op.create_table(
        "users",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("hashed_password", sa.Text(), nullable=False),
        sa.Column("goal_calories", sa.Integer(), nullable=True),
        sa.Column("goal_protein_g", sa.Numeric(6, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )


def downgrade() -> None:
    op.drop_table("users")
