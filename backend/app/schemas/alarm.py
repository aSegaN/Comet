from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

Severity = Literal["INFO", "WARN", "MAJOR", "CRITICAL"]
Status = Literal["OPEN", "CLEARED", "ACK"]

class AlarmOut(BaseModel):
    id: int
    site_id: str
    site_name: str
    alarm_code: str
    alarm_label: str
    severity: Severity
    status: Status
    started_at: datetime
    cleared_at: Optional[datetime] = None
    acked_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AlarmListResponse(BaseModel):
    items: list[AlarmOut]
    page: int = Field(ge=1)
    page_size: int
    total: int
