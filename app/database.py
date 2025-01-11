from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Для SQLite используйте aiosqlite
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///database.db"
# Для PostgreSQL используйте asyncpg
# SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://user:password@postgresserver/db"

# Создаем асинхронный движок
engine = create_async_engine(SQLALCHEMY_DATABASE_URL)

# Создаем асинхронную сессию
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)