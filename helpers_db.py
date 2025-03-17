from fastapi import HTTPException, status
from models import SessionLocal, UserData, SessionData, FileData  
from schemas import UserInfo, SessionInfo
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_user_entry(db: Session, userInfo: UserInfo):
    db_entry = UserData(email = userInfo.email, device_id = userInfo.device_id)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)

def create_session_entry(db: Session, sessionToken: str, userId: int):
    db_entry = SessionData(session_token = sessionToken, user_id = userId)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)

def create_file_entry(db: Session, userId: int, fileName: str, filePath: str):
    db_entry = FileData(user_id = userId, file_name = fileName, file_path = filePath)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)

def get_user_by_info(db: Session, userInfo: UserInfo) -> UserData:
    return (
        db.query(UserData)
        .filter(UserData.email == userInfo.email, UserData.device_id == userInfo.device_id)
        .first()
    )

def get_user_id_from_device_id(db: Session, sessionInfo: SessionInfo) -> int:
    user = db.query(UserData).filter(UserData.device_id == sessionInfo.device_id).first()
    if user is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Your user details could not be retrieved."
        )

    return user.user_id

def get_user_id_from_session_token(db: Session, sessionToken: str) -> int:
    user_id = db.query(SessionData).filter(SessionData.session_token == sessionToken).first()
    if user_id is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Your user details could not be retrieved."
        )

    return user_id

def doesMatchSessionToken(db: Session, sessionToken: str) -> bool:
    return (
        db.query(SessionData)
        .filter(SessionData.session_token == sessionToken)
        .first()
        is not None
    )

def get_file_path_for_download(db: Session, user_id: str, file_name: str) -> str:
    file_path = db.query(FileData).filter(FileData.user_id == user_id, FileData.file_name == file_name).first()
    if file_path is None:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Your requested file does not exist."
        )

    return file_path