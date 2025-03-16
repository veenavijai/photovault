from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class UserData(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key = True, index = True)
    email = Column(String)
    device_id = Column(String)
    sessions = relationship("SessionData", back_populates = "user")
    files = relationship("FileData", back_populates = "user")

class SessionData(Base):
    __tablename__ = "sessions"
    session_token = Column(String,  primary_key = True, index = True)
    # This is hashed
    four_digit_code = Column(String)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    device_id = Column(String)
    user = relationship("UserData", back_populates = "sessions")

class FileData(Base):
    __tablename__ = "files"
    file_id = Column(Integer, primary_key = True, index = True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    file_name = Column(String)
    user = relationship("UserData", back_populates = "files")