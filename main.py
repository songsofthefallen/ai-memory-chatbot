from fastapi import FastAPI, HTTPException
from routers import conversation, auth
from exception_handler import exception_handler


app = FastAPI()

app.add_exception_handler( #when HTTPException is raised call exception_handler
    HTTPException,
    exception_handler
)

app.include_router(auth.router)
app.include_router(conversation.router)


