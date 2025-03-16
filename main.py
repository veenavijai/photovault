from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
import hashlib
import random

import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, Session


app = FastAPI()


DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = sqlalchemy.orm.declarative_base()


class UserData(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key = True, index = True)
    email = Column(String)
    device_id = Column(String)

class SessionData(Base):
    __tablename__ = "sessions"
    session_token = Column(String,  primary_key = True, index = True)
    # TODO have the hashed version of this?
    four_digit_code = Column(String)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    device_id = Column(String)

class FileData(Base):
    __tablename__ = "files"
    file_id = Column(Integer, primary_key = True, index = True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    file_name = Column(String)


class UserInfo(BaseModel):
    email: str
    device_id: str

class SessionInfo(BaseModel):
    device_id: str
    code: str

class FileInfo(BaseModel):
    file_name: str


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
    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "You are not a registered user."
        )

    code = random.randint(1000, 9999)
    hashedCode = secure_hash(str(code))
    # Store the hashed code for security
    # Ideally the key is the user_id AND device_id
    pending_codes[userInfo.device_id] = hashedCode
    return code

'''
# Create mock database users
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
'''

# Store temporary 4 digit codes in memory
pending_codes = {}


'''

def create_session(db: Session, sessionInfo: SessionInfo):
    # TODO can I call it session?

    db_entry = Session(sessionToken:)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

    
@app.post("/auth/code/verify")
async def generate_session_token(sessionInfo: SessionInfo):
    now = datetime.datetime.now(tz = datetime.timezone.utc)
    currentTime = int(now.timestamp())
    
    # A random seed makes this token harder to regenerate
    # Risk: xxhash is not cryptographically secure.
    # Could be replaced by SHA-256 and truncation to 16 char
    hasher = xxhash.xxh64(seed = currentTime)
    
    # TODO needs error handling
    # TODO how can this be encrypted further?
    # TODO Is it safer to use a longer hash and truncate it?
    hasher.update(str(sessionInfo.code) + sessionInfo.device_id)
    sessionToken = hasher.hexdigest()
    return {"session_token": sessionToken}

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