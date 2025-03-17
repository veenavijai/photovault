
from fastapi import HTTPException, status

from helpers_db import get_user_id_from_device_id
from schemas import UserInfo, SessionInfo, FileInfo

def validate_user_info(userInfo: UserInfo):
    if not userInfo or not userInfo.email or not userInfo.device_id:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Please enter a valid request."
        )

    # TODO this is pretty naive, we can use regex to match an email template.
    if not isinstance(userInfo.email, str):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Please enter a valid email ID."
        )

    if not isinstance(userInfo.device_id, str):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Please enter a valid device ID."
        )
    
def validate_session_info(sessionInfo: SessionInfo):
    if not sessionInfo or not sessionInfo.code or not sessionInfo.device_id:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Please enter a valid request."
        )

    if not isinstance(sessionInfo.device_id, str):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Please enter a valid device ID."
        )

    if not isinstance(sessionInfo.code, str):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Please enter a 4-digit code."
        )

def validate_device_id_and_code(db, hashedCode: str, sessionInfo: SessionInfo, pending_codes: dict) -> int:# 
    user_id = get_user_id_from_device_id(db, sessionInfo)

    if not sessionInfo.device_id in pending_codes:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Please request a new 4-digit code."
        )

    if pending_codes[sessionInfo.device_id] != hashedCode:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "You have entered an incorrect 4-digit code."
        )
    
    return user_id