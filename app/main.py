from fastapi import FastAPI, Depends, HTTPException

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import yaml

from . import crud, models, schemas
from .database import SessionLocal, engine
from .openai_service import Assistant

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

with open("config.yaml", 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

assistant = Assistant(**config)

def get_db():
    with SessionLocal() as db:
        yield db
        
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_user(db=db, user=user)
    except IntegrityError as e:
        db.rollback()
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=400, detail="User with this login already exists")
        else:
            raise HTTPException(status_code=500, detail=f"Database error {e}")

@app.get("/users/", response_model=list[schemas.User])
def get_users(db: Session = Depends(get_db)):
    user = crud.get_users(db=db)    
    return user

@app.get("/users/{login}", response_model=schemas.User)
def get_user_by_login(login: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_login(db=db, login=login)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@app.delete("/users/", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    deleted_entry = crud.delete_user_by_id(db, user_id)
    if deleted_entry is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return deleted_entry

@app.post("/sessions/", response_model=schemas.ChatSession)
def create_session(session: schemas.ChatSessionCreate, db: Session = Depends(get_db)):
    return crud.create_chat_session(db=db, session=session)

@app.get("/sessions/ids", response_model=list[int])
def get_chat_session_ids(db: Session = Depends(get_db)):
    session_ids = crud.get_all_chat_session_ids(db)
    return session_ids

@app.get("/sessions/{session_id}/messages", response_model=list[schemas.ChatMessage])
def get_messages_by_session_id(session_id: int, db: Session = Depends(get_db)):
    session = crud.get_chat_session(db, session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session with id={session_id} not found")
    
    return session.messages

@app.delete("/sessions/{session_id}", response_model=schemas.ChatSession)
def delete_session(session_id: int, db: Session = Depends(get_db)):
    deleted_entry = crud.delete_chat_session(db, session_id)
    if deleted_entry is None:
        raise HTTPException(status_code=404, detail=f"Session with id={session_id} not found")
    
    return deleted_entry

@app.post("/sessions/{session_id}/messages/", response_model=schemas.ChatMessage)
def create_message(session_id: int, message: schemas.ChatMessageCreate, db: Session = Depends(get_db)):
    session = crud.get_chat_session(db, session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    glossary = crud.get_glossary_entries(db)

    messages = [{"role": msg.role, "content": msg.content} for msg in session.messages]
    messages.append({"role": "user", "content": message.content})
    
    response_content, input_token_count, output_token_count = assistant(messages, glossary)

    crud.increment_user_tokens(db, session.user_id, input_token_count, output_token_count)
    
    response_message = schemas.ChatMessageBase(role="assistant", content=response_content)
    input_message = schemas.ChatMessageBase(role="user", content=message.content)

    crud.create_chat_message(db=db, message=input_message, session_id=session_id)
    return crud.create_chat_message(db=db, message=response_message, session_id=session_id)


@app.post("/glossary/", response_model=schemas.Glossary)
def create_glossary_entry(glossary: schemas.GlossaryCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_glossary_entry(db=db, glossary=glossary)
    except IntegrityError as e:
        db.rollback()
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=400, detail="This term already registered")
        else:
            raise HTTPException(status_code=500, detail=f"Database error {e}")

@app.delete("/glossary/", response_model=schemas.Glossary)
def delete_glossary_entry(glossary: schemas.GlossaryDelete, db: Session = Depends(get_db)):
    deleted_entry = crud.delete_glossary_entry(db, glossary.id)
    if deleted_entry is None:
        raise HTTPException(status_code=404, detail="Term not found")
    
    return deleted_entry

@app.get("/glossary/", response_model=list[schemas.Glossary])
def read_general_glossary(db: Session = Depends(get_db)):
    glossary = crud.get_general_glossary(db)
    return glossary

@app.get("/glossary/{user_id}", response_model=list[schemas.Glossary])
def read_user_glossary(user_id: int, db: Session = Depends(get_db)):
    glossary = crud.get_user_glossary(db, user_id)
    return glossary

@app.post("/train_samples/", response_model=schemas.TrainSample)
def create_train_sample(train_sample: schemas.TrainSampleCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_train_sample(db=db, train_sample=train_sample)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error {e}")

@app.delete("/train_samples/{sample_id}", response_model=schemas.TrainSample)
def delete_train_sample(sample_id: int, db: Session = Depends(get_db)):
    deleted_entry = crud.delete_train_sample(db, sample_id)
    if deleted_entry is None:
        raise HTTPException(status_code=404, detail="Train sample not found")
    
    return deleted_entry

@app.get("/train_samples/", response_model=list[schemas.TrainSample])
def read_train_samples(db: Session = Depends(get_db)):
    train_samples = crud.get_train_samples(db)
    return train_samples

@app.get("/train_samples/{sample_id}", response_model=schemas.TrainSample)
def get_train_sample_by_id(sample_id: int, db: Session = Depends(get_db)):
    train_sample = crud.get_train_sample_by_id(db, sample_id)
    if train_sample is None:
        raise HTTPException(status_code=404, detail="Train sample not found")
    
    return train_sample

@app.post("/train_samples/upload", response_model=dict)
def upload_dataset(db: Session = Depends(get_db)):
    train_samples = crud.get_train_samples(db)
    glossary = crud.get_glossary_entries(db)
    result = assistant.upload_dataset(train_samples, glossary)
    return {"status": "success", "message": "Messages uploaded", "result": result}

