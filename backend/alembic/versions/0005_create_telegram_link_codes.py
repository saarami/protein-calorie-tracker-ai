"""create telegram_link_codes

Revision ID: 0005_create_telegram_link_codes
Revises: 0004_create_telegram_links
Create Date: 2026-01-22
"""

from alembic import op
import sqlalchemy as sa

revision = "0005_create_telegram_link_codes"
down_revision = "0004_create_telegram_links"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "telegram_link_codes",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code_hash", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("code_hash", name="uq_telegram_link_codes_code_hash"),
    )
    op.create_index("ix_tlc_user_expires", "telegram_link_codes", ["user_id", "expires_at"])
    op.create_index("ix_tlc_expires_at", "telegram_link_codes", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_tlc_expires_at", table_name="telegram_link_codes")
    op.drop_index("ix_tlc_user_expires", table_name="telegram_link_codes")
    op.drop_table("telegram_link_codes")
