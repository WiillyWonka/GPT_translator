from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
def read_chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/glossary", response_class=HTMLResponse)
def read_glossary_page(request: Request):
    return templates.TemplateResponse("glossary.html", {"request": request})

def get_db():
    with SessionLocal() as db:
        yield db

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
    # Попытка удаления записи из глоссария
    deleted_entry = crud.delete_chat_session(db, session_id)
    
    # Если запись не найдена, возвращаем ошибку 404
    if deleted_entry is None:
        raise HTTPException(status_code=404, detail=f"Session with id={session_id} not found")
    
    # Возвращаем удаленную запись
    return deleted_entry

@app.post("/sessions/{session_id}/messages/", response_model=schemas.ChatMessage)
def create_message(session_id: int, message: schemas.ChatMessageCreate, db: Session = Depends(get_db)):
    session = crud.get_chat_session(db, session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    glossary = crud.get_glossary_entries(db)

    # Получаем все сообщения из сессии
    messages = [{"role": msg.role, "content": msg.content} for msg in session.messages]
    messages.append({"role": "user", "content": message.content})
    
    # Генерируем ответ от ChatGPT
    response_content = assistant(messages, glossary)
    
    # Сохраняем ответ в базу данных
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
            raise HTTPException(status_code=400, detail="This term aleady registered")
        else:
            raise HTTPException(status_code=500, detail=f"Database error {e}")

@app.delete("/glossary/", response_model=schemas.Glossary)
def delete_glossary_entry(glossary_term: schemas.GlossaryDelete, db: Session = Depends(get_db)):
    # Попытка удаления записи из глоссария
    deleted_entry = crud.delete_glossary_entry(db, glossary_term.term)
    
    # Если запись не найдена, возвращаем ошибку 404
    if deleted_entry is None:
        raise HTTPException(status_code=404, detail="Term not found")
    
    # Возвращаем удаленную запись
    return deleted_entry

@app.get("/glossary/", response_model=list[schemas.Glossary])
def read_glossary(db: Session = Depends(get_db)):
    glossary = crud.get_glossary_entries(db)
    return glossary