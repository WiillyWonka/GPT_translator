from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine
from .openai_service import generate_response

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/sessions/", response_model=schemas.ChatSession)
def create_session(session: schemas.ChatSessionCreate, db: Session = Depends(get_db)):
    return crud.create_chat_session(db=db, session=session)

@app.post("/sessions/{session_id}/messages/", response_model=schemas.ChatMessage)
def create_message(session_id: int, message: schemas.ChatMessageCreate, db: Session = Depends(get_db)):
    session = crud.get_chat_session(db, session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Получаем все сообщения из сессии
    messages = [{"role": msg.role, "content": msg.content} for msg in session.messages]
    messages.append({"role": "user", "content": message.content})
    
    # Генерируем ответ от ChatGPT
    response_content = generate_response(messages)
    
    # Сохраняем ответ в базу данных
    response_message = schemas.ChatMessageCreate(role="assistant", content=response_content)
    return crud.create_chat_message(db=db, message=response_message, session_id=session_id)

@app.post("/glossary/", response_model=schemas.Glossary)
def create_glossary_entry(glossary: schemas.GlossaryCreate, db: Session = Depends(get_db)):
    return crud.create_glossary_entry(db=db, glossary=glossary)

@app.get("/glossary/", response_model=list[schemas.Glossary])
def read_glossary(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    glossary = crud.get_glossary_entries(db, skip=skip, limit=limit)
    return glossary