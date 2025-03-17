from helpers_db import create_user_entry
from models import Base, engine, SessionLocal, UserData
from schemas import UserInfo

# Creates mock database users - run this script only once
Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    if db.query(UserData).count() == 0:
        user_1 = UserInfo(email = "user1@gmail.com", device_id = "ABCDEF")
        user_2 = UserInfo(email = "user2@gmail.com", device_id = "XYZ")
        user_3 = UserInfo(email = "user1@gmail.com", device_id = "456")

        create_user_entry(db, user_1)
        create_user_entry(db, user_2)
        create_user_entry(db, user_3)

finally:
    db.close()