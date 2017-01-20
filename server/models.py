from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from server.database import Base

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, server_default=func.now())
    event_type = Column(String(2))
