import bcrypt
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from schemas import RegisterUser, LoginUser
from database import get_db
from models import User
from logger import logger
from services.all_services import find_user_name
from security.jwt import get_token


router = APIRouter()


@router.post('/register')
def register_user(user: RegisterUser, db = Depends(get_db)):

    hashed_pass = bcrypt.hashpw(
        user.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    db_user = User(username = user.username, email = user.email, password = hashed_pass)

    db.add(db_user)
    db.commit()

    logger.info("User Registered Successfully")

    raise HTTPException(status_code=200, detail="User Registered Successfully")

@router.post('/login') 
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)): #oauth expect from data not json so no pydantic model

    stored_user = find_user_name(form_data.username, db)

    if not stored_user:
        raise HTTPException(status_code=404, detail="User Not Found")
    
    if not bcrypt.checkpw(
        form_data.password.encode("utf-8"),
        stored_user.password.encode("utf-8")
    ):
        raise HTTPException(status_code=401, detail="Incorrect Password")

    token = get_token(stored_user)

    return token
