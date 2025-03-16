from fastapi import FastAPI
from pydantic import BaseModel
import datetime
import xxhash

app = FastAPI()

class CustomerInfo(BaseModel):
    email: str
    device_id: str

@app.post("/auth/code/request")
async def generate_code(customerInfo: CustomerInfo):
    return hash_multiple_keys(customerInfo.email, customerInfo.device_id)

def hash_multiple_keys(*keys):
    # TODO security risk - should a fixed tuple always result in the same hash?
    # If a bad actor had access to the 4 digit code,
    # they could generate the session token and get access.
    # This should be generated non-deterministically
    return hash(tuple(sorted(keys))) % 10000

@app.post("/auth/code/verify")
async def generate_session_token(code: int, device_id: str):
    now = datetime.datetime.now(tz = datetime.timezone.utc)
    currentTime = int(now.timestamp())
    
    # A random seed makes this token harder to regenerate
    hasher = xxhash.xxh64(seed = currentTime)
    
    # TODO needs error handling
    # TODO how can this be encrypted further?
    # TODO Is it safer to use a longer hash and truncate it?
    hasher.update(str(code) + device_id)
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

    # Have a DB associating user to the file

@app.get("/file/:file_name")
async def download_file(sessionToken: str, file_name: str):
     # Check if token is present

    # Is the token well-formed

    # Is the token expired?

    # Verify token is associated with this user 
    
    # Validate that file_name is associated with user
    # Might be better to associate each file with a key here, 
    # Because different users can use the same file_name
    
    # Retrieve file_name from DB
    
    # Return file byte stream and status code      
