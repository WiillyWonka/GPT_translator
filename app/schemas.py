from pydantic import BaseModel
from typing import List

class ChatMessageBase(BaseModel):
    role: str
    content: str

class ChatMessageCreate(ChatMessageBase):
    pass

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

class GlossaryCreate(GlossaryBase):
    pass

class Glossary(GlossaryBase):
    id: int

    class Config:
        orm_mode = True