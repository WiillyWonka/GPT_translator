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
    session_ids = [session.id for session in db.query(models.ChatSession).all()]
    return session_ids

def delete_chat_session(db: Session, session_id: int):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if session is None:
        return None
    db.delete(session)
    db.commit()
    return session

def create_chat_message(db: Session, message: schemas.ChatMessageBase, session_id: int):
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
    entry = db.query(models.Glossary).filter(models.Glossary.term == term).first()
    if entry is None:
        return None
    db.delete(entry)
    db.commit()
    return entry

def get_glossary_entries(db: Session):
    return db.query(models.Glossary).all()

def create_train_sample(db: Session, train_sample: schemas.TrainSampleCreate):
    db_train_sample = models.TrainSample(**train_sample.model_dump())
    db.add(db_train_sample)
    db.commit()
    db.refresh(db_train_sample)
    return db_train_sample

def delete_train_sample(db: Session, sample_id: int):
    entry = db.query(models.TrainSample).filter(models.TrainSample.id == sample_id).first()
    if entry is None:
        return None
    db.delete(entry)
    db.commit()
    return entry

def get_train_samples(db: Session):
    return db.query(models.TrainSample).all()

def get_train_sample_by_id(db: Session, sample_id: int):
    return db.query(models.TrainSample).filter(models.TrainSample.id == sample_id).first()

