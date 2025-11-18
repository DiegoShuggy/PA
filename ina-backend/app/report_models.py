# report_models.py
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class ReportPeriod(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly" 
    BIWEEKLY = "biweekly"
    TRIWEEKLY = "triweekly"
    MONTHLY = "monthly"

class ReportRequest(BaseModel):
    period_days: int
    include_pdf: bool = False
    advanced_pdf: bool = True  # Usar generador avanzado por defecto
    email: Optional[str] = None

class EmailRequest(BaseModel):
    email: str
    period_days: int
    report_type: str = "basic"
    advanced_pdf: bool = True  # Usar reporte avanzado por defecto