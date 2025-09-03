from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text
from app.db.base_class import Base

class ValuationRun(Base):
    __tablename__ = "valuation_runs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(64), index=True, nullable=False)       # e.g. "PRJ-001"
    mode = Column(String(16), nullable=False)                          # "equity" | "credit"
    engine = Column(String(32), nullable=False, default="valuation")
    inputs = Column(JSON, nullable=False)
    result = Column(JSON, nullable=False)
    nav_per_token = Column(Float, nullable=True)
    base_value = Column(Float, nullable=True)                          # mid/base value
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    