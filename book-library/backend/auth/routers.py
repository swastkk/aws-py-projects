from fastapi import APIRouter, Depends, FastAPI

from auth import authentication

app = FastAPI()
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.get("/token")
def get_token():
    return authentication.generate_token()
