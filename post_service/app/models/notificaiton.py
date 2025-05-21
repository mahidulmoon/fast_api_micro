from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from database import Base

class Notification(Base):
    __tablename__ = 'Wo_Notifications'
    
    id = Column(Integer, primary_key=True, index=True)
    notifier_id = Column(Integer, ForeignKey('Wo_Users.user_id'), index=True)
    recipient_id = Column(Integer, ForeignKey('Wo_Users.user_id'), index=True)
    post_id = Column(Integer, ForeignKey('Wo_Posts.id'), default=0)
    reply_id = Column(Integer, default=0)
    comment_id = Column(Integer, default=0)
    page_id = Column(Integer, default=0)
    group_id = Column(Integer, default=0)
    group_chat_id = Column(Integer, default=0)
    event_id = Column(Integer, default=0)
    thread_id = Column(Integer, default=0)
    blog_id = Column(Integer, default=0)
    story_id = Column(Integer, default=0)
    seen_pop = Column(Integer, default=0)
    type = Column(String(255), default='')
    type2 = Column(String(32), default='')
    text = Column(Text)
    url = Column(String(255), default='')
    full_link = Column(String(1000), default='')
    seen = Column(Integer, default=0)
    sent_push = Column(Integer, default=0)
    admin = Column(Integer, default=0)
    time = Column(Integer, default=0)