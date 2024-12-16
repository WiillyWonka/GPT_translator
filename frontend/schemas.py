from pydantic import BaseModel, Field
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class User(BaseModel):
    """
    Модель пользователя.
    """
    id: int = Field(..., description="Уникальный идентификатор пользователя")
    login: str = Field(..., description="Логин пользователя")
    role: UserRole = Field(..., description="Роль пользователя (admin или user)")
    total_input_tokens: int = Field(0, ge=0, description="Общее количество входных токенов")
    total_output_tokens: int = Field(0, ge=0, description="Общее количество выходных токенов")

    class Config:
        use_enum_values = True  # Использовать строковые значения Enum при сериализации

class Glossary(BaseModel):
    """
    Модель для терминологического словаря.
    """
    id: int = Field(..., description="Уникальный идентификатор записи в словаре")
    term: str = Field(..., min_length=1, description="Термин")
    translation: str = Field(..., min_length=1, description="Перевод термина")
    comment: str = Field(default="", description="Комментарий к термину")
    user_id: int = Field(..., ge=1, description="Идентификатор пользователя, создавшего запись")