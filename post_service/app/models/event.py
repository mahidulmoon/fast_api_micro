from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Date, Time
from sqlalchemy.sql import func
from database import Base

class Event(Base):
    __tablename__ = 'Wo_Events'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), default='')
    location = Column(String(300), default='')
    description = Column(Text)
    start_date = Column(Date)
    start_time = Column(Time)
    end_date = Column(Date)
    end_time = Column(Time)
    poster_id = Column(Integer, ForeignKey('Wo_Users.user_id'))
    cover = Column(String(500), default='upload/photos/d-cover.jpg')
    property_id = Column(String(250))
    property_home_type = Column(String(255))
    archive = Column(String(255), default='0')
    pin = Column(String(255), default='0')