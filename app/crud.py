from sqlalchemy.orm import Session
from . import models, schemas

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(login=user.login, role=user.role, total_input_tokens=0, total_output_tokens=0)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session):
    users = db.query(models.User).all()
    return users

def get_user_by_id(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user

def get_user_by_login(db: Session, login: str):
    user = db.query(models.User).filter(models.User.login == login).first()
    return user

def delete_user_by_id(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return user
    return None

def increment_user_tokens(db: Session, user_id: int, input_token_count: int, output_token_count: int):
    """
    Инкрементирует количество токенов пользователя.

    :param db: Сессия базы данных SQLAlchemy.
    :param user_id: Идентификатор пользователя.
    :param input_token_count: Количество входных токенов для добавления.
    :param output_token_count: Количество выходных токенов для добавления.
    """
    # Получаем пользователя по его ID
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise ValueError(f"Пользователь с ID {user_id} не найден.")

    # Инкрементируем количество токенов
    user.total_input_tokens += input_token_count
    user.total_output_tokens += output_token_count

    # Фиксируем изменения в базе данных
    db.commit()
    db.refresh(user)

    return user

def create_chat_session(db: Session, session: schemas.ChatSessionCreate):
    db_session = models.ChatSession(user_id=session.user_id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_chat_session(db: Session, session_id: int):
    return db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()

def get_all_chat_session_ids(db: Session):
    session_ids = [session.id for session in db.query(models.ChatSession).all()]
    return session_ids

def delete_chat_session(db: Session, session_id: int):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if session is None:
        return None
    db.delete(session)
    db.commit()
    return session

def create_chat_message(db: Session, message: schemas.ChatMessageBase, session_id: int):
    db_message = models.ChatMessage(**message.model_dump(), session_id=session_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def create_glossary_entry(db: Session, glossary: schemas.GlossaryCreate):
    db_glossary = models.Glossary(**glossary.model_dump())
    db.add(db_glossary)
    db.commit()
    db.refresh(db_glossary)
    return db_glossary

def delete_glossary_entry(db: Session, glossary_id):
    entry = db.query(models.Glossary).filter(models.Glossary.id == glossary_id).first()
    if entry is None:
        return None
    db.delete(entry)
    db.commit()
    return entry

def get_glossary_entries(db: Session):
    return db.query(models.Glossary).all()

def get_user_glossary(db: Session, user_id: int):
    """
    Получает все экземпляры глоссария, которые относятся к пользователю с указанным id

    :param db: Сессия базы данных SQLAlchemy.
    :param user_id: Идентификатор пользователя.
    :return: Список экземпляров глоссария.
    """
    # Запрос для получения глоссария пользователя с указанным id и всех администраторов
    glossary_items = db.query(models.Glossary).join(models.User).filter(
        (models.User.id == user_id)
    ).all()

    return glossary_items

def get_general_glossary(db: Session):
    """
    Получает все экземпляры глоссария, которые относятся ко всем пользователям с ролью admin.

    :param db: Сессия базы данных SQLAlchemy.
    :return: Список экземпляров глоссария.
    """
    # Запрос для получения глоссария пользователя с указанным id и всех администраторов
    glossary_items = db.query(models.Glossary).join(models.User).filter(
        (models.User.role == "admin")
    ).all()

    return glossary_items

def create_train_sample(db: Session, train_sample: schemas.TrainSampleCreate):
    db_train_sample = models.TrainSample(**train_sample.model_dump())
    db.add(db_train_sample)
    db.commit()
    db.refresh(db_train_sample)
    return db_train_sample

def delete_train_sample(db: Session, sample_id: int):
    entry = db.query(models.TrainSample).filter(models.TrainSample.id == sample_id).first()
    if entry is None:
        return None
    db.delete(entry)
    db.commit()
    return entry

def get_train_samples(db: Session):
    return db.query(models.TrainSample).all()

def get_train_sample_by_id(db: Session, sample_id: int):
    return db.query(models.TrainSample).filter(models.TrainSample.id == sample_id).first()

