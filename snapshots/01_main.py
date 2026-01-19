from fastapi import FastAPI

app = FastAPI()

async def read_root():
    return {
        "message":"Hello World"
    }