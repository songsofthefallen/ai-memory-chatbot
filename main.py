from fastapi import FastAPI
from routers import conversation, auth

app = FastAPI()

app.include_router(auth.router)
app.include_router(conversation.router)


