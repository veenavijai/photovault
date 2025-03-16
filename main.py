from fastapi import FastAPI, Depends, HTTPException, status
from models import Base, engine, SessionLocal, UserData, SessionData, FileData  
from schemas import UserInfo, SessionInfo, FileInfo
import datetime
import hashlib
import secrets
import xxhash

from sqlalchemy.orm import Session


app = FastAPI()

# Database-related helper functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_user(db: Session, userInfo: UserInfo):
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

def secure_hash(key: str) -> str:
    # Python's hash() or any deterministic hash might be a security risk 
    # If a bad actor had access to the 4 digit code, they could 
    # deterministically generate the session token and get access.
    return hashlib.sha256(key.encode('utf-8')).hexdigest()

@app.post("/auth/code/request")
async def generate_and_store_code(userInfo: UserInfo, db: Session = Depends(get_db)):
    # Check if user is in DB first
    user = get_user_by_info(db, userInfo)
    if user is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "You are not a registered user."
        )

    code = str(secrets.randbelow(10000)).zfill(4)
    hashedCode = secure_hash(code)
    # Store the hashed code for security
    # Ideally the key is the user_id AND device_id
    pending_codes[userInfo.device_id] = hashedCode
    print(f'Your 4-digit code is: {code}')
    return code


# Store temporary 4 digit codes in memory
pending_codes = {}

# Creates mock database users - run only once
Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    if db.query(UserData).count() == 0:
        user_1 = UserInfo(email = "user1@gmail.com", device_id = "ABCDEF")
        user_2 = UserInfo(email = "user2@gmail.com", device_id = "XYZ")
        user_3 = UserInfo(email = "user1@gmail.com", device_id = "456")

        create_user(db, user_1)
        create_user(db, user_2)
        create_user(db, user_3)

finally:
    db.close()

def generate_session_token(sessionInfo: SessionInfo) -> str:
    # A random seed like current time makes this token harder to regenerate
    now = datetime.datetime.now(tz = datetime.timezone.utc)
    currentTime = int(now.timestamp())

    # Risk: xxhash is not cryptographically secure, could be replaced by SHA-256 and truncation to 16 char
    # TODO Is it safe to directly truncate a longer hash? It may increase risk of collisions.
    hasher = xxhash.xxh64(seed = currentTime)
    hasher.update(str(sessionInfo.code) + sessionInfo.device_id)
    return hasher.hexdigest()

def get_user_id_from_device_id(db: Session, sessionInfo: SessionInfo) -> int:
    user = db.query(UserData).filter(UserData.device_id == sessionInfo.device_id).first()
    if user is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Your user details could not be retrieved."
        )

    return user.user_id

def validate_device_id_and_code(db, hashedCode: str, sessionInfo: SessionInfo) -> int:

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
    
def create_session_entry(db: Session, userId: int, sessionInfo: SessionInfo, hashedCode: str, sessionToken: str):
    db_entry = SessionData(session_token = sessionToken, four_digit_code = hashedCode, device_id = sessionInfo.device_id, user_id = userId)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    

@app.post("/auth/code/verify")
async def verify_four_digit_code(sessionInfo: SessionInfo, db: Session = Depends(get_db)):
    if sessionInfo is None or sessionInfo.code is None:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Your request is missing a four digit code."
        )
    
    # Validate whether user ID is retrievable, device ID is registered and code is correct
    hashedCode = secure_hash(sessionInfo.code)
    user_id = validate_device_id_and_code(db, hashedCode, sessionInfo)
    
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
    create_session_entry(db, user_id, sessionInfo, hashedCode, sessionToken)
    
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