# photovault
Authenticated photo uploads and downloads.

## Setup instructions

```
git clone https://github.com/veenavijai/photovault.git
cd photovault
python3 -m venv .venv
pip3 install -r requirements.txt
python3 create_mock_DB.py
```

### Spin up a web server

```
uvicorn main:app --reload
```

### API testing

Swagger UI: http://127.0.0.1:8000/docs#/

## Feature list
- POST API which accepts user information and generates a 4-digit PIN
- POST API which accepts the user's device ID and the 4-digit PIN to generate a session token
- POST API which accepts previously generated session token and a file bytestream and uploads file after user authentication
- GET API which accepts previously generated session token and a file name, and downloads file after user authentication

## High-level design choices

### Tools 

- Web Framework: I chose FastAPI over Flask since it supported asynchronous APIs. Moreover, REST APIs seemed much easier to test since FastAPI offered in-built data validation with Pydantic schemas. Thankfully, this paid off because error messages were straightforward.
- Asynchronous Server Gateway Interface: uvicorn. I needed an application server to handle async requests, and uvicorn + FastAPI had great documentation online.
- Database: SQLite. Storing user information locally felt like a no-no, considering there were several entities and relationships to model, and security is the biggest priority. So, I chose SQLite which didn't require me to spin up another server and was as lightweight as possible.
- Schema modeling: Pydantic (built-in).
- UI for testing: I tried Swagger UI to see what it was like. The UI was so clean and the auto-generated documentation was fantastic. I could see all the response body and error codes and it was very user-friendly.

### Data modeling

- UserData: I decided on a user_id to identify users in case they changed their email later was useful. I also didn't want to pass around their emails later on while authenticating them. user_id was a natural choice of foreign key to have in other databases.
- SessionData: Initially, I stored device_id and the 4-digit code and then realized I don't need them. I needed this intermediate table to help me lookup the user for auth.
- FileData: file_id seemed like a better choice of primary key compared to a sanitized file name. I also stored the file path at time of upload so it didn't have to be regenerated at time of download.
 
```
class UserData(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key = True, index = True)
    email = Column(String)
    device_id = Column(String)

class SessionData(Base):
    __tablename__ = "sessions"
    session_token = Column(String,  primary_key = True, index = True)
    user_id = Column(Integer, ForeignKey("users.user_id"))

class FileData(Base):
    __tablename__ = "files"
    file_id = Column(Integer, primary_key = True, index = True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    file_name = Column(String)
    file_path = Column(String)
```

## Required changes to move from a local prototype to production-ready code with the same feature set

- For scalability and concurrency: A web server that allows for easy horizontal scaling + allows for caching, like Nginx. An ASGI + reverse proxy seem to be a powerful combination to have a production-ready web app serving a large number of requests.
- A DB with more features and scaling capabilities
- Containerization: Although I installed Docker locally, I didn't have time to containerize this app. It would make setup easier, and also allow for great flexibility if I wanted to switch dependencies/OS. Running `uvicorn --reload` should be restricted to a local prototype.
- Persistence in the DB: Could be achieved by Docker again.
- Dedicated database to store 4-digit codes that are pending session token generation. For speed, I chose to use a local map in memory.
- A rate-limiter to throttle excess requests - 429 is not handled in this MVP.

## Testing description
- Print statements, Swagger UI, testing various "non-happy paths" to validate HTTP status codes

## Known risks and areas of improvement
- I used xxhash64 to generate the session token, which is not meant for cryptographic hashing but instead for good performance and few collisions, and generated a 16-character hash code that fit these specs. I used a random seed i.e. `datetime.now()` to make it less worse. I read about alternatives like SHA-256 and MD-5, but I was worried that truncating a longer hash to 16 characters would greatly increase collision risk. This doesn't matter for a locally running prototype, but it seems important for a large-scale application.
- Several more fields should likely be hashed before storing them directly in the DB and querying for them, specifically user_id, session_token 
- In the validation functions, regexes would be a stricter check, esp. for fields like email.
- In the file download API, there are potential vulnerabilities. For example, a bad actor could keep generating session codes and hit the API with 'popular' file names. If that session code simply existed in the DB due to some past activity from any user (since session codes cannot expire) and the file name matched, the bad actor would have rendered this application not secure. To avoid this, there should be strict expiry limits on sign-in codes and session tokens. This could also be somewhat mitigated through rate limiting.
- The file path for each user can be unique and user a user-based hash, instead of a common `uploads/` folder.

## My feature bucket list 

- POST API to add new users to the DB instead of a one-time script, to make it more demo-able too
- Deletion of a file, and of the whole account
- Session token and 4-digit code expiry: 5 minutes or something similar
- Restricting the uploaded file to only certain file formats and capping the size
- File organization into folders with separate locks and share-able passwords

## Credits

- Google Search
- FastAPI docs
- Geeksforgeeks tutorials on REST APIs + database integration with FastAPI
- Medium blogs
- Coffee
