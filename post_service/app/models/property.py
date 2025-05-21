from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from database import Base

class Property(Base):
    __tablename__ = 'Wo_Add_Properties'
    
    id = Column(Integer, primary_key=True, index=True)
    property_url = Column(Text)
    imgSrc = Column(Text)
    homeStatus = Column(String(250))
    bedrooms = Column(String(250))
    bathrooms = Column(String(250))
    homeType = Column(String(250))
    livingArea = Column(String(250))
    streetAddress = Column(String(250))
    city = Column(String(250))
    state = Column(String(250))
    zipcode = Column(String(250))
    brokerName = Column(String(250))
    memberFullName = Column(String(250))
    memberStateLicense = Column(String(250))
    description = Column(Text)
    price = Column(String(250))
    currency = Column(String(250))
    all_photos = Column(Text)
    status = Column(String(250))
    user_id = Column(Integer, ForeignKey('Wo_Users.user_id'))
    datetime = Column(DateTime, server_default=func.now())
    longitude = Column(Integer)
    latitude = Column(Integer)