"""create alarms table

Revision ID: 001_create_alarms
Revises:
Create Date: 2025-09-24

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001_create_alarms"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "alarms",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("site_id", sa.String(length=64), nullable=False),
        sa.Column("site_name", sa.String(length=255), nullable=False),
        sa.Column("alarm_code", sa.String(length=128), nullable=False),
        sa.Column("alarm_label", sa.String(length=255), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("started_at", postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("cleared_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("acked_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("source_file", sa.String(length=255), nullable=True),
        sa.Column("extras", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_alarms_site_id", "alarms", ["site_id"])
    op.create_index("ix_alarms_severity", "alarms", ["severity"])
    op.create_index("ix_alarms_status", "alarms", ["status"])
    op.create_index("ix_alarms_started_at", "alarms", ["started_at"])
    op.create_unique_constraint("uq_alarms_natural", "alarms", ["site_id", "alarm_code", "started_at"])

def downgrade():
    op.drop_constraint("uq_alarms_natural", "alarms", type_="unique")
    op.drop_index("ix_alarms_started_at", table_name="alarms")
    op.drop_index("ix_alarms_status", table_name="alarms")
    op.drop_index("ix_alarms_severity", table_name="alarms")
    op.drop_index("ix_alarms_site_id", table_name="alarms")
    op.drop_table("alarms")
