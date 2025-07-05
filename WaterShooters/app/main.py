from fastapi import FastAPI,HTTPException,Request

from app.database import  engine
from app.models.base import Base
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import register_routes

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.detail,
            "status_code": exc.status_code,
        },
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_routes(app)


@app.get('/')
def home():
    return {"hello": "world"}



