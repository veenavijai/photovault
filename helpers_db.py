from fastapi import HTTPException, status
from models import SessionLocal, UserData, SessionData, FileData  
from schemas import UserInfo, SessionInfo, FileInfo
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

def create_session_entry(db: Session, sessionToken: str, userId: int):
    db_entry = SessionData(session_token = sessionToken, user_id = userId)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)