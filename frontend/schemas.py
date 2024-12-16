from pydantic import BaseModel

class User(BaseModel):
    id: int
    login: str
    role: str
    total_input_tokens: int
    total_output_tokens: int