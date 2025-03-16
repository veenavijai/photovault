from fastapi import FastAPI
from pydantic import BaseModel
import random
import datetime
import xxhash

app = FastAPI()

class CustomerInfo(BaseModel):
    email: str
    device_id: str

@app.post("/auth/code/request")
async def generate_code(customerInfo: CustomerInfo):
    code = random.randint(1000, 9999)
    # TODO Store this somewhere
    codeHashed = hash_key(code)
    return code

def hash_key(key):
    # TODO security risk - should a fixed tuple always result in the same hash?
    # If a bad actor had access to the 4 digit code,
    # they could generate the session token and get access.
    # This should be generated non-deterministically
    return hash(key) % 10000



@app.post("/auth/code/verify")
async def generate_session_token(code: int, device_id: str):
    now = datetime.datetime.now(tz = datetime.timezone.utc)
    currentTime = int(now.timestamp())
    
    # A random seed makes this token harder to regenerate
    # Risk: xxhash is not cryptographically secure.
    # Could be replaced by SHA-256 and truncation to 16 char
    hasher = xxhash.xxh64(seed = currentTime)
    
    # TODO needs error handling
    # TODO how can this be encrypted further?
    # TODO Is it safer to use a longer hash and truncate it?
    hasher.update(str(code) + device_id)
    sessionToken = hasher.hexdigest()
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