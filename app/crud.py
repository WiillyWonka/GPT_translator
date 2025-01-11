from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models, schemas

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    db_user = models.User(login=user.login, role=user.role, total_input_tokens=0, total_output_tokens=0)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_users(db: AsyncSession):
    result = await db.execute(select(models.User))
    users = result.scalars().all()
    return users

async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    user = result.scalars().first()
    return user

async def get_user_by_login(db: AsyncSession, login: str):
    result = await db.execute(select(models.User).filter(models.User.login == login))
    user = result.scalars().first()
    return user

async def delete_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    user = result.scalars().first()
    if user:
        await db.delete(user)
        await db.commit()
        return user
    return None

async def increment_user_tokens(db: AsyncSession, user_id: int, input_token_count: int, output_token_count: int):
    """
    Инкрементирует количество токенов пользователя.

    :param db: Асинхронная сессия базы данных SQLAlchemy.
    :param user_id: Идентификатор пользователя.
    :param input_token_count: Количество входных токенов для добавления.
    :param output_token_count: Количество выходных токенов для добавления.
    """
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise ValueError(f"Пользователь с ID {user_id} не найден.")

    user.total_input_tokens += input_token_count
    user.total_output_tokens += output_token_count

    await db.commit()
    await db.refresh(user)

    return user

async def create_chat_session(db: AsyncSession, session: schemas.ChatSessionCreate):
    db_session = models.ChatSession(user_id=session.user_id)
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    return db_session

async def get_chat_session(db: AsyncSession, session_id: int):
    result = await db.execute(select(models.ChatSession).filter(models.ChatSession.id == session_id))
    session = result.scalars().first()
    return session

async def get_all_chat_session_ids(db: AsyncSession):
    result = await db.execute(select(models.ChatSession))
    session_ids = [session.id for session in result.scalars().all()]
    return session_ids

async def delete_chat_session(db: AsyncSession, session_id: int):
    result = await db.execute(select(models.ChatSession).filter(models.ChatSession.id == session_id))
    session = result.scalars().first()
    if session is None:
        return None
    await db.delete(session)
    await db.commit()
    return session

async def create_chat_message(db: AsyncSession, message: schemas.ChatMessageBase, session_id: int):
    db_message = models.ChatMessage(**message.model_dump(), session_id=session_id)
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)
    return db_message

async def create_glossary_entry(db: AsyncSession, glossary: schemas.GlossaryCreate):
    db_glossary = models.Glossary(**glossary.model_dump())
    db.add(db_glossary)
    await db.commit()
    await db.refresh(db_glossary)
    return db_glossary

async def delete_glossary_entry(db: AsyncSession, glossary_id: int):
    result = await db.execute(select(models.Glossary).filter(models.Glossary.id == glossary_id))
    entry = result.scalars().first()
    if entry is None:
        return None
    await db.delete(entry)
    await db.commit()
    return entry

async def get_glossary_entries(db: AsyncSession):
    result = await db.execute(select(models.Glossary))
    glossary_entries = result.scalars().all()
    return glossary_entries

async def get_user_glossary(db: AsyncSession, user_id: int):
    """
    Получает все экземпляры глоссария, которые относятся к пользователю с указанным id.

    :param db: Асинхронная сессия базы данных SQLAlchemy.
    :param user_id: Идентификатор пользователя.
    :return: Список экземпляров глоссария.
    """
    result = await db.execute(
        select(models.Glossary)
        .join(models.User)
        .filter(models.User.id == user_id)
    )
    glossary_items = result.scalars().all()
    return glossary_items

async def get_general_glossary(db: AsyncSession):
    """
    Получает все экземпляры глоссария, которые относятся ко всем пользователям с ролью admin.

    :param db: Асинхронная сессия базы данных SQLAlchemy.
    :return: Список экземпляров глоссария.
    """
    result = await db.execute(
        select(models.Glossary)
        .join(models.User)
        .filter(models.User.role == "admin")
    )
    glossary_items = result.scalars().all()
    return glossary_items

async def create_train_sample(db: AsyncSession, train_sample: schemas.TrainSampleCreate):
    db_train_sample = models.TrainSample(**train_sample.model_dump())
    db.add(db_train_sample)
    await db.commit()
    await db.refresh(db_train_sample)
    return db_train_sample

async def delete_train_sample(db: AsyncSession, sample_id: int):
    result = await db.execute(select(models.TrainSample).filter(models.TrainSample.id == sample_id))
    entry = result.scalars().first()
    if entry is None:
        return None
    await db.delete(entry)
    await db.commit()
    return entry

async def get_train_samples(db: AsyncSession):
    result = await db.execute(select(models.TrainSample))
    train_samples = result.scalars().all()
    return train_samples

async def get_train_sample_by_id(db: AsyncSession, sample_id: int):
    result = await db.execute(select(models.TrainSample).filter(models.TrainSample.id == sample_id))
    train_sample = result.scalars().first()
    return train_sample