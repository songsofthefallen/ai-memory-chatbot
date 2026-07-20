from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, func, desc, Text
from sqlalchemy.orm import relationship
from database import Base, engine

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    conversations = relationship('Conversation', back_populates='user', cascade='all, delete-orphan')
    tokens = relationship('RefreshToken', back_populates='user', cascade='all, delete-orphan')

class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    create_at = Column(DateTime, server_default=func.now())
    latest_activity = Column(DateTime)

    user = relationship('User', back_populates='conversations')
    messages = relationship('Message', back_populates='conversation', cascade='all, delete-orphan', order_by=lambda: desc(Message.latest_activity)) #used in response model to order the list of messages

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    role = Column(String(100), nullable=False)
    content = Column(Text)
    create_at = Column(DateTime, server_default=func.now())
    latest_activity = Column(DateTime,default=func.now(),onupdate=func.now()) #set it as time created or updated

    conversation = relationship('Conversation', back_populates='messages')

class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'
    id = Column(Integer, primary_key=True)
    token = Column(String(255), unique=True, nullable=False)
    jti = Column(String(64))
    user_id = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(DateTime)
    revoked = Column(Boolean, default=False)

    user = relationship('User', back_populates='tokens')

Base.metadata.create_all(engine)



