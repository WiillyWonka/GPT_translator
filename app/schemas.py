from pydantic import BaseModel
from typing import List

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
    user_id: str

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSession(ChatSessionBase):
    id: int
    messages: List[ChatMessage] = []

    class Config:
        orm_mode = True

class GlossaryBase(BaseModel):
    term: str
    translation: str
    comment: str

class GlossaryCreate(GlossaryBase):
    pass

class GlossaryDelete(BaseModel):
    term: str

class Glossary(GlossaryBase):
    id: int

    class Config:
        orm_mode = True