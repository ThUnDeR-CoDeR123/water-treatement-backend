from fastapi import FastAPI,HTTPException,Request
from app.routes.users import tokenRouter
from app.routes.plant import plantrouter
from app.routes.log import logRouter
from app.routes.images import imageRouter
from app.routes.forgetPasswordRoutes import forgetRouter
from app.routes.plantequipment import router as plantequipment_router
from app.routes.plantchemical import router as plantchemical_router
from app.routes.plantflowparameter import router as plantflowparameter_router
from app.routes.plantequipment import router as plantequipment_router

from app.database import  engine
from app.models.base import Base
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from fastapi.responses import JSONResponse
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

app.include_router(plantrouter)
app.include_router(logRouter)
app.include_router(tokenRouter)
app.include_router(imageRouter)
app.include_router(forgetRouter)
app.include_router(plantequipment_router)
app.include_router(plantchemical_router)
app.include_router(plantflowparameter_router)

@app.get('/')
def home():
    return {"hello": "world"}



