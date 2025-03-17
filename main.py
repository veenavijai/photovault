from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pathvalidate import sanitize_filename
from sqlalchemy.orm import Session

from helpers_db import get_db, get_user_by_info, create_session_entry, get_user_id_from_session_token, create_file_entry, get_file_path_for_download
from helpers_hash import generate_session_token, secure_hash
from helpers_validation import validate_user_info, validate_session_info, validate_device_id_and_code, validate_auth_format, validate_file, validate_file_path
from schemas import UserInfo, SessionInfo

import os
import secrets

app = FastAPI()
app.mount("/uploads", StaticFiles(directory = "uploads"), name = "uploads")
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# Store temporary 4 digit codes in memory. This should be in a DB for a production system.
pending_codes = {}

@app.post("/auth/code/request")
async def generate_and_store_code(userInfo: UserInfo, db: Session = Depends(get_db)):
    validate_user_info(userInfo)

    user = get_user_by_info(db, userInfo)
    if user is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "You are not a registered user."
        )

    code = str(secrets.randbelow(10000)).zfill(4)
    hashedCode = secure_hash(code)
    # Store the hashed code for security
    # TODO there may be a better key than just device_id
    pending_codes[userInfo.device_id] = hashedCode
    print(f'Your 4-digit code is: {code}')
    return code
    
@app.post("/auth/code/verify")
async def verify_four_digit_code(sessionInfo: SessionInfo, db: Session = Depends(get_db)):    
    validate_session_info(sessionInfo)
    
    # Validate whether user ID is retrievable, device ID is registered and code is correct
    hashedCode = secure_hash(sessionInfo.code)
    user_id = validate_device_id_and_code(db, hashedCode, sessionInfo, pending_codes)
    
    '''
    print(f'Pending codes in hashed form are:\n')
    for keys, value in pending_codes.items():
        print(f'keys: {keys}, hashedCode: {value}\n')
    '''
    
    # If we have reached here, our device ID and code are valid
    # Clear this element from our local map
    del pending_codes[sessionInfo.device_id]
    # print(f"\nDeleted {sessionInfo.code} from list of pending codes")

    sessionToken = generate_session_token(sessionInfo)
    create_session_entry(db, sessionToken, user_id)
    
    return {"session_token": sessionToken}

@app.post("/file/{file_name}")
async def upload_file(file_name: str, sessionToken: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    validate_auth_format(db, sessionToken)
    user_id = get_user_id_from_session_token(db, sessionToken)

    # TODO add session expiry as a feature. (5 minutes seems reasonable)
    # TODO validate that input is only of certain formats, maybe jpg, png, mov
    # TODO keep size limits on input?

    sanitized_filename = sanitize_filename(file_name)
    validate_file(sanitized_filename)
    
    file_path = os.path.join("uploads", sanitized_filename)
    # Delete pre-existing file with this path, if any
    if os.path.exists(file_path):
        os.remove(file_path)

    try:
        with open(file_path, "wb") as f:
            while contents := file.file.read(1024 * 1024):
                f.write(contents)
        file.file.close()
        db = next(get_db())
        try:
            create_file_entry(db, user_id, file_name, file_path)
        finally: 
            db.close()
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = str(e)
        )
    
    return {"message": "File upload was successful!"}

@app.get("/file/{file_name}")
async def download_file(file_name: str, sessionToken: str, db: Session = Depends(get_db)):
    validate_auth_format(db, sessionToken)
    user_id = get_user_id_from_session_token(db, sessionToken)

    sanitized_filename = sanitize_filename(file_name)
    validate_file(sanitized_filename)

    # Verify file_name is associated with this user
    file_path = get_file_path_for_download(db, user_id, sanitized_filename)
    validate_file_path(file_path)

    # Return file byte stream
    def data_generator(file_path: str):
        with open(file_path, "rb") as f:
            while chunk := f.read(1024):
                yield chunk

    # TODO need to guard against invalid types
    return StreamingResponse(data_generator(file_path), media_type="image/jpeg")