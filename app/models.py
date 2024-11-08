from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role = Column(String)  # "user" or "assistant"
    content = Column(Text)

    session = relationship("ChatSession", back_populates="messages")

class Glossary(Base):
    __tablename__ = "glossary"

    id = Column(Integer, primary_key=True, index=True)
    term = Column(String, unique=True, index=True)
    translation = Column(String)
    comment = Column(String)

class TrainSample(Base):
    __tablename__ = "train_samples"

    id = Column(Integer, primary_key=True, index=True)
    foreign_text = Column(Text, index=True)
    translation = Column(Text)
