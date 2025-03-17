# minikeepsafe
MVP for a Mini Keepsafe

## Setup instructions

```
git clone https://github.com/veenavijai/minikeepsafe.git
cd minikeepsafe
python3 -m venv .venv
pip3 install -r requirements.txt
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

## Required changes to move from a local prototype to production-ready code

## Testing description

## Known risks and areas of improvement

## Feature bucket list 



