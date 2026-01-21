from fastapi import FastAPI

app = FastAPI()
from version import __version__

version_map ={
    "0.0.1": "v1"
}

version = version_map[__version__]
@app.get(f"/{version}/")
def read_root():
    return {"Hello": "World from fastAPI in Docker!"}

@app.get(f"/{version}/greet")
def greet():
    return {"message": "Hello from the greet endpoint!"}
