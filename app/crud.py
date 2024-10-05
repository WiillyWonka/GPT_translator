from sqlalchemy.orm import Session
from . import models, schemas

def create_chat_session(db: Session, session: schemas.ChatSessionCreate):
    db_session = models.ChatSession(user_id=session.user_id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_chat_session(db: Session, session_id: int):
    return db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()

def create_chat_message(db: Session, message: schemas.ChatMessageCreate, session_id: int):
    db_message = models.ChatMessage(**message.model_dump(), session_id=session_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def create_glossary_entry(db: Session, glossary: schemas.GlossaryCreate):
    db_glossary = models.Glossary(**glossary.model_dump())
    db.add(db_glossary)
    db.commit()
    db.refresh(db_glossary)
    return db_glossary

def get_glossary_entries(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Glossary).offset(skip).limit(limit).all()