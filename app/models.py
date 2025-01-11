from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, index=True)
    role = Column(Enum("admin", "user", name="user_role"), nullable=False)  # "admin" or "user"
    total_input_tokens = Column(Integer, default=0)
    total_output_tokens = Column(Integer, default=0)

    # Связь с ChatSession
    chat_sessions = relationship("ChatSession", back_populates="user")
    glossary = relationship("Glossary", back_populates="user")

    def __repr__(self):
        return f"User#{self.id} (login: {self.login}, role: {self.role})"

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    messages = relationship("ChatMessage", back_populates="session", lazy="selectin")

    # Связь с User
    user = relationship("User", back_populates="chat_sessions")
    
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
    term = Column(String, index=True)
    translation = Column(String)
    comment = Column(String)

    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    # Связь с User
    user = relationship("User", back_populates="glossary")

class TrainSample(Base):
    __tablename__ = "train_samples"

    id = Column(Integer, primary_key=True, index=True)
    foreign_text = Column(Text, index=True)
    translation = Column(Text)
