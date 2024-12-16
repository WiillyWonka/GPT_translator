from pydantic import BaseModel
from typing import List

class UserCreate(BaseModel):
    login: str
    role: str

class UserBase(UserCreate):
    total_input_tokens: int
    total_output_tokens: int

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class ChatMessageBase(BaseModel):
    role: str
    content: str

class ChatMessageCreate(BaseModel):
    content: str

class ChatMessage(ChatMessageBase):
    id: int
    session_id: int

    class Config:
        orm_mode = True

class ChatSessionBase(BaseModel):
    user_id: int
    messages: List[ChatMessage] = []

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSession(ChatSessionBase):
    id: int

    class Config:
        orm_mode = True

class GlossaryBase(BaseModel):
    term: str
    translation: str
    comment: str
    user_id: int

class GlossaryCreate(GlossaryBase):
    pass

class GlossaryDelete(BaseModel):
    id: int

class Glossary(GlossaryBase):
    id: int

    class Config:
        orm_mode = True

class TrainSampleBase(BaseModel):
    foreign_text: str
    translation: str

class TrainSampleCreate(TrainSampleBase):
    pass

class TrainSampleDelete(BaseModel):
    id: int

class TrainSample(TrainSampleBase):
    id: int

    class Config:
        orm_mode = True
