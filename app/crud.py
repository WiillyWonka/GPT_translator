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

def get_all_chat_session_ids(db: Session):
    # Получаем все сессии и извлекаем их идентификаторы
    session_ids = [session.id for session in db.query(models.ChatSession).all()]
    
    # Возвращаем список идентификаторов
    return session_ids

def delete_chat_session(db: Session, session_id: int):
    # Находим сессию по идентификатору
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    
    # Если сессия не найдена, возвращаем None
    if session is None:
        return None
    
    # Удаляем сессию из базы данных
    db.delete(session)
    db.commit()
    
    # Возвращаем удаленную сессию
    return session

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

def delete_glossary_entry(db: Session, term: str):
    # Находим запись по термину
    entry = db.query(models.Glossary).filter(models.Glossary.term == term).first()
    
    # Если запись не найдена, возвращаем None
    if entry is None:
        return None
    
    # Удаляем запись из базы данных
    db.delete(entry)
    db.commit()
    
    # Возвращаем удаленную запись
    return entry

def get_glossary_entries(db: Session):
    return db.query(models.Glossary).all()