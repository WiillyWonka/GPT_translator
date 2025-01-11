import asyncio
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from contextlib import asynccontextmanager
import yaml

from . import crud, schemas
from .database import AsyncSessionLocal, init_models
from .openai_service import Assistant


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    await init_models()  # Initialize the database
    yield

app = FastAPI(lifespan=lifespan)

with open("config.yaml", 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

assistant = Assistant(**config)

async def get_db():
    async with AsyncSessionLocal() as db:
        yield db

@app.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.create_user(db=db, user=user)
    except IntegrityError as e:
        await db.rollback()
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=400, detail="User with this login already exists")
        else:
            raise HTTPException(status_code=500, detail=f"Database error {e}")

@app.get("/users/", response_model=list[schemas.User])
async def get_users(db: AsyncSession = Depends(get_db)):
    users = await crud.get_users(db=db)
    return users

@app.get("/users/{login}", response_model=schemas.User)
async def get_user_by_login(login: str, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_login(db=db, login=login)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/users/", response_model=schemas.User)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    deleted_entry = await crud.delete_user_by_id(db, user_id)
    if deleted_entry is None:
        raise HTTPException(status_code=404, detail="User not found")
    return deleted_entry

@app.post("/sessions/", response_model=schemas.ChatSession)
async def create_session(session: schemas.ChatSessionCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_chat_session(db=db, session=session)

@app.get("/sessions/ids", response_model=list[int])
async def get_chat_session_ids(db: AsyncSession = Depends(get_db)):
    session_ids = await crud.get_all_chat_session_ids(db)
    return session_ids

@app.get("/sessions/{session_id}/messages", response_model=list[schemas.ChatMessage])
async def get_messages_by_session_id(session_id: int, db: AsyncSession = Depends(get_db)):
    session = await crud.get_chat_session(db, session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session with id={session_id} not found")
    return session.messages

@app.delete("/sessions/{session_id}", response_model=schemas.ChatSession)
async def delete_session(session_id: int, db: AsyncSession = Depends(get_db)):
    deleted_entry = await crud.delete_chat_session(db, session_id)
    if deleted_entry is None:
        raise HTTPException(status_code=404, detail=f"Session with id={session_id} not found")
    return deleted_entry

@app.post("/sessions/{session_id}/messages/", response_model=schemas.ChatMessage)
async def create_message(session_id: int, message: schemas.ChatMessageCreate, db: AsyncSession = Depends(get_db)):
    session = await crud.get_chat_session(db, session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    glossary = await crud.get_glossary_entries(db)

    messages = [{"role": msg.role, "content": msg.content} for msg in session.messages]
    messages.append({"role": "user", "content": message.content})
    
    response_content, input_token_count, output_token_count = await assistant(messages, glossary)

    await crud.increment_user_tokens(db, session.user_id, input_token_count, output_token_count)
    
    response_message = schemas.ChatMessageBase(role="assistant", content=response_content)
    input_message = schemas.ChatMessageBase(role="user", content=message.content)

    await crud.create_chat_message(db=db, message=input_message, session_id=session_id)
    return await crud.create_chat_message(db=db, message=response_message, session_id=session_id)

@app.post("/glossary/", response_model=schemas.Glossary)
async def create_glossary_entry(glossary: schemas.GlossaryCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.create_glossary_entry(db=db, glossary=glossary)
    except IntegrityError as e:
        await db.rollback()
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=400, detail="This term already registered")
        else:
            raise HTTPException(status_code=500, detail=f"Database error {e}")

@app.delete("/glossary/", response_model=schemas.Glossary)
async def delete_glossary_entry(glossary: schemas.GlossaryDelete, db: AsyncSession = Depends(get_db)):
    deleted_entry = await crud.delete_glossary_entry(db, glossary.id)
    if deleted_entry is None:
        raise HTTPException(status_code=404, detail="Term not found")
    return deleted_entry

@app.get("/glossary/", response_model=list[schemas.Glossary])
async def read_general_glossary(db: AsyncSession = Depends(get_db)):
    glossary = await crud.get_general_glossary(db)
    return glossary

@app.get("/glossary/{user_id}", response_model=list[schemas.Glossary])
async def read_user_glossary(user_id: int, db: AsyncSession = Depends(get_db)):
    glossary = await crud.get_user_glossary(db, user_id)
    return glossary

@app.post("/train_samples/", response_model=schemas.TrainSample)
async def create_train_sample(train_sample: schemas.TrainSampleCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.create_train_sample(db=db, train_sample=train_sample)
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error {e}")

@app.delete("/train_samples/{sample_id}", response_model=schemas.TrainSample)
async def delete_train_sample(sample_id: int, db: AsyncSession = Depends(get_db)):
    deleted_entry = await crud.delete_train_sample(db, sample_id)
    if deleted_entry is None:
        raise HTTPException(status_code=404, detail="Train sample not found")
    return deleted_entry

@app.get("/train_samples/", response_model=list[schemas.TrainSample])
async def read_train_samples(db: AsyncSession = Depends(get_db)):
    train_samples = await crud.get_train_samples(db)
    return train_samples

@app.get("/train_samples/{sample_id}", response_model=schemas.TrainSample)
async def get_train_sample_by_id(sample_id: int, db: AsyncSession = Depends(get_db)):
    train_sample = await crud.get_train_sample_by_id(db, sample_id)
    if train_sample is None:
        raise HTTPException(status_code=404, detail="Train sample not found")
    return train_sample

@app.post("/train_samples/upload", response_model=dict)
async def upload_dataset(db: AsyncSession = Depends(get_db)):
    train_samples = await crud.get_train_samples(db)
    glossary = await crud.get_glossary_entries(db)
    result = await assistant.upload_dataset(train_samples, glossary)
    return {"status": "success", "message": "Messages uploaded", "result": result}