from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from database import Base

class Comment(Base):
    __tablename__ = 'Wo_Comments'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('Wo_Users.user_id'), index=True)
    page_id = Column(Integer, default=0)
    post_id = Column(Integer, ForeignKey('Wo_Posts.id'), index=True)
    text = Column(Text)
    record = Column(String(255), default='')
    c_file = Column(String(255), default='')
    time = Column(Integer, default=0)