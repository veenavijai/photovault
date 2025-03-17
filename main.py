from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from helpers_db import get_db, get_user_by_info, create_session_entry
from helpers_hash import generate_session_token, secure_hash
from helpers_validation import validate_user_info, validate_session_info, validate_device_id_and_code
from schemas import UserInfo, SessionInfo, FileInfo

import secrets

app = FastAPI()

# Store temporary 4 digit codes in memory
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

    # Store session information in SessionData DB
    create_session_entry(db, sessionToken, user_id)
    
    return {"session_token": sessionToken}

'''

@app.post("/file/:file_name")
async def upload_file(sessionToken: str, file_name: str):
    # Check if token is present

    # Is the token well-formed

    # Is the token expired?

    # Verify token is associated with this user 

    # Validate file type and size

    # Store the file on the cloud/disk
    file_content = await file.read()

    # Have a DB associating user to the file

@app.get("/file/:file_name")
async def download_file(sessionToken: str, file_name: str):
     # Check if token is present

    # Is the token well-formed

    # Is the token expired?

    # Verify token is associated with this user
    # Device ID can be different in this case
    
    # Validate that file_name is associated with user
    # Might be better to associate each file with a key here, 
    # Because different users can use the same file_name
    
    # Retrieve file_name from DB
    
    # Return file byte stream and status code      
'''
