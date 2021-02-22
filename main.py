from fastapi import FastAPI, Depends, HTTPException
from starlette import status
from starlette.requests import Request

from config import get_settings
from db import models
from db.main import engine
from router.dependencies import get_kafka
from router.routes import api_router

settings = get_settings()

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


async def check_auth_middleware(request: Request):
    if settings.environment == 'production':
        auth_token = request.headers.get('Authorization')
        if auth_token != settings.auth_token or auth_token is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@app.on_event("shutdown")
def shutdown_event():
    producer = get_kafka()
    producer.close()


app.include_router(api_router, dependencies=[Depends(check_auth_middleware)])
