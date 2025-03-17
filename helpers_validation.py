from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from helpers_db import get_user_id_from_device_id, doesMatchSessionToken
from schemas import UserInfo, SessionInfo

import os

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

def validate_device_id_and_code(db: Session, hashedCode: str, sessionInfo: SessionInfo, pending_codes: dict) -> int:
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

def validate_auth_format(db: Session, sessionToken: str):
    if not sessionToken or not isinstance(sessionToken, str) or len(sessionToken) != 16:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "You have entered an invalid session token."
        )
    
    if not doesMatchSessionToken(db, sessionToken):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Please enter a valid session token."
        )
    
def validate_file(file_name: str):
    if not file_name:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Please name the file you want to upload."
        )

    if not isinstance(file_name, str):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Please enter a valid file name."
        )
    
def validate_file_contents(contents):
    if not contents:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "You are trying to upload an empty file."
        )

def validate_file_path(file_path: str):
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Your file path could not be found!"
        )