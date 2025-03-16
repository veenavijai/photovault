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
    hasher = xxhash.xxh64(seed = currentTime)
    hasher.update(str(code) + device_id)
    sessionToken = hasher.hexdigest()
    return {"session_token": sessionToken}
