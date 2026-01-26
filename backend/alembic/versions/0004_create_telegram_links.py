"""create telegram_links

Revision ID: 0004_create_telegram_links
Revises: 0003_create_meal_items
Create Date: 2026-01-22
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_create_telegram_links"
down_revision = "0003_create_meal_items"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "telegram_links",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("linked_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("user_id", name="uq_telegram_links_user_id"),
        sa.UniqueConstraint("chat_id", name="uq_telegram_links_chat_id"),
    )


def downgrade() -> None:
    op.drop_table("telegram_links")
