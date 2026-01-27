from fastapi import FastAPI, APIRouter, Depends
from auth import authentication
app = FastAPI()
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from db import get_db
from auth.routers import auth_router
from books.routers import book_router

app = FastAPI()

@app.middleware("http")
async def auth_validator(request: Request, call_next):
    print("Request URL:", request.url.path)
    if request.url.path not in ["/auth/token", "/docs", "/openapi.json", "/"]:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
        token = auth_header.split(" ")[1]
        validation_result = authentication.validate_token({"authorizationToken": token})
        if validation_result.status_code != 200:
            return validation_result

    return await call_next(request)


app.include_router(auth_router, tags=["Authentication"])
app.include_router(book_router, tags=["Books"])


@app.get("/")
def read_root():
    return {"status": "healthy"}