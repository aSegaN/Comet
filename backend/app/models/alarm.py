from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, JSON, Index
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Alarm(Base):
    __tablename__ = "alarms"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    site_id: Mapped[str] = mapped_column(String(64), nullable=False)
    site_name: Mapped[str] = mapped_column(String(255), nullable=False)
    alarm_code: Mapped[str] = mapped_column(String(128), nullable=False)
    alarm_label: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)   # INFO/WARN/MAJOR/CRITICAL
    status: Mapped[str] = mapped_column(String(16), nullable=False)     # OPEN/CLEARED/ACK
    started_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    cleared_at: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    acked_at: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    source_file: Mapped[str | None] = mapped_column(String(255))
    extras: Mapped[dict | None] = mapped_column(JSON)

    created_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_alarms_site_id", "site_id"),
        Index("ix_alarms_severity", "severity"),
        Index("ix_alarms_status", "status"),
        Index("ix_alarms_started_at", "started_at"),
        # clé logique pour l’upsert
        Index("uq_alarms_natural", "site_id", "alarm_code", "started_at", unique=True),
    )
