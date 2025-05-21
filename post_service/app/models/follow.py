from sqlalchemy import Column, Integer, ForeignKey
from database import Base

class Follow(Base):
    __tablename__ = 'Wo_Followers'
    
    id = Column(Integer, primary_key=True, index=True)
    following_id = Column(Integer, ForeignKey('Wo_Users.user_id'), index=True)
    follower_id = Column(Integer, ForeignKey('Wo_Users.user_id'), index=True)
    is_typing = Column(Integer, default=0)
    active = Column(Integer, default=1)
    notify = Column(Integer, default=0)
    time = Column(Integer, default=0)