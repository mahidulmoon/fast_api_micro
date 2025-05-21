from sqlalchemy import Column, Integer, ForeignKey
from database import Base

class Like(Base):
    __tablename__ = 'Wo_Likes'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('Wo_Users.user_id'), index=True)
    post_id = Column(Integer, ForeignKey('Wo_Posts.id'), index=True)