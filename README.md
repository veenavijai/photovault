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

Overall: 
- I tried to understand Keepsafe's tech stack first and learn why each component was necessary/the preferred option.
- I aimed to find a sweet spot between technologies that would help me prototype quickly, but also convert the code to production-level if I had time later.

- Web Framework: I chose FastAPI over Flask since it supported asynchronous APIs. Moreover, REST APIs seemed much easier to test since FastAPI offered in-built data validation with Pydantic schemas. Thankfully, this paid off because error messages were straightforward.
- Asynchronous Server Gateway Interface: uvicorn. I needed an application server to handle async requests, and uvicorn + FastAPI had great documentation online.
- Database: SQLite. Storing user information locally even for an MVP felt like a no-no, considering there were several entities and relationships to model, and security is the biggest priority. So, I chose SQLite which didn't require me to spin up another server and was as lightweight as possible.
- Data modeling: Pydantic (built-in).
- UI for testing: I tried Swagger UI to see what it was like. The UI was so clean and the auto-generated documentation was fantastic. I could see all the response body and error codes and it was very user-friendly.

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


## Feature bucket list 

## Credits

