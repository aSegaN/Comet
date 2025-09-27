from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from typing import Annotated, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.repositories.alarms import list_alarms
from app.schemas.alarm import AlarmListResponse, AlarmOut

router = APIRouter()

Page = Annotated[int, Query(ge=1, description="Page (>=1)")]
PageSize = Annotated[int, Query(ge=10, le=200, description="Taille page [10..200]")]

@router.get("/alarms", response_model=AlarmListResponse)
async def get_alarms(
    page: Page = 1,
    page_size: PageSize = 25,
    severity: Optional[list[str]] = Query(default=None),
    status: Optional[list[str]] = Query(default=None),
    q: Optional[str] = None,
    from_: Optional[datetime] = Query(default=None, alias="from"),
    to: Optional[datetime] = None,
    ordering: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    items, total = await list_alarms(
        session=session,
        page=page,
        page_size=page_size,
        severity=severity,
        status=status,
        q=q,
        date_from=from_,
        date_to=to,
        ordering=ordering,
    )
    return {"items": items, "page": page, "page_size": page_size, "total": total}
