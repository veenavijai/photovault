from schemas import SessionInfo

import datetime
import hashlib
import xxhash


def secure_hash(key: str) -> str:
    # Python's hash() or any deterministic hash might be a security risk 
    # If a bad actor had access to the 4 digit code, they could 
    # deterministically generate the session token and get access.
    return hashlib.sha256(key.encode('utf-8')).hexdigest()

def generate_session_token(sessionInfo: SessionInfo) -> str:
    # A random seed like current time makes this token harder to regenerate
    now = datetime.datetime.now(tz = datetime.timezone.utc)
    currentTime = int(now.timestamp())

    # Risk: xxhash is not cryptographically secure, could be replaced by SHA-256 and truncation to 16 char
    # TODO Is it safe to directly truncate a longer hash? It may increase risk of collisions.
    hasher = xxhash.xxh64(seed = currentTime)
    hasher.update(sessionInfo.code + sessionInfo.device_id)
    return hasher.hexdigest()