from __future__ import annotations
from sqlalchemy import select, func, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence
from datetime import datetime
from app.models.alarm import Alarm

ALLOWED_ORDER = {
    "started_at": Alarm.started_at,
    "severity": Alarm.severity,
    "site_name": Alarm.site_name,
}

def normalize_ordering(ordering: str | None):
    if not ordering:
        return desc(Alarm.started_at)
    col = ordering.lstrip("-")
    if col not in ALLOWED_ORDER:
        return desc(Alarm.started_at)
    return desc(ALLOWED_ORDER[col]) if ordering.startswith("-") else asc(ALLOWED_ORDER[col])

async def list_alarms(
    session: AsyncSession,
    page: int = 1,
    page_size: int = 25,
    severity: list[str] | None = None,
    status: list[str] | None = None,
    q: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    ordering: str | None = None,
) -> tuple[Sequence[Alarm], int]:
    stmt = select(Alarm)
    count_stmt = select(func.count(Alarm.id))

    # filtres
    if severity:
        stmt = stmt.where(Alarm.severity.in_(severity))
        count_stmt = count_stmt.where(Alarm.severity.in_(severity))
    if status:
        stmt = stmt.where(Alarm.status.in_(status))
        count_stmt = count_stmt.where(Alarm.status.in_(status))
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(Alarm.site_name.ilike(like), Alarm.alarm_label.ilike(like), Alarm.alarm_code.ilike(like)))
        count_stmt = count_stmt.where(or_(Alarm.site_name.ilike(like), Alarm.alarm_label.ilike(like), Alarm.alarm_code.ilike(like)))
    if date_from:
        stmt = stmt.where(Alarm.started_at >= date_from)
        count_stmt = count_stmt.where(Alarm.started_at >= date_from)
    if date_to:
        stmt = stmt.where(Alarm.started_at <= date_to)
        count_stmt = count_stmt.where(Alarm.started_at <= date_to)

    stmt = stmt.order_by(normalize_ordering(ordering)).offset((page - 1) * page_size).limit(page_size)

    result = await session.execute(stmt)
    items = result.scalars().all()

    total = (await session.execute(count_stmt)).scalar_one()
    return items, total
