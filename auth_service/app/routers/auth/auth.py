from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...utils import response
from ...database import SessionLocal
from ...schema import user_auth_schema
from ...models.wo_user import User
import os
from passlib.context import CryptContext
from sqlalchemy import or_
from ...logger import logger
from datetime import datetime, timedelta
from jose import JWTError, jwt


SECRET_KEY= os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY not set in environment.")
    combined = password + SECRET_KEY
    return pwd_context.hash(combined)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/user_register")
def user_register(user_input: user_auth_schema.RegisterUser,db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(
            or_(User.email == user_input.email, User.username == user_input.username)
            ).first()
        if db_user:
            logger.error(f"Email or Username already registered")
            return response.error_response("Email or Username already registered",None,400)
        
        hashed_pw = hash_password(user_input.password)
        new_user = User(
            email=user_input.email, 
            password=hashed_pw,
            username = user_input.username,
            first_name = user_input.first_name,
            last_name = user_input.last_name,
            address = user_input.address,
            phone_number = user_input.phone_number,
            city = user_input.city,
            state = user_input.state,
            country_name = user_input.country_name
            )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"user successfully registered")
        return response.success_response("user successfully registered",{},201)
    
    except Exception as e:
        logger.error(str(e))
        return response.error_response(str(e),None,400)

@router.post("/login")
def login(user_input: user_auth_schema.LoginUserInput,db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.email == user_input.email).first()
        if not db_user:
            logger.error(f"No user found using this email")
            return response.error_response("No user found using this email",None,400)
        
        if not verify_password(user_input.password + os.getenv("SECRET_KEY"), db_user.password):
            logger.warning(f"Login failed: wrong password for {user_input.email}")
        
        access_token = create_access_token(
            data={"sub": db_user.email},  # sub = subject (email)
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return_json = {
            "access_token" : access_token,
            "token_type" : "bearer",
            "user_data" : {
                "email" : db_user.email,
                "first_name" : db_user.first_name,
                "last_name" : db_user.last_name,
                "admin" : db_user.admin
            }
        }

        return response.success_response("successfully logged in.",return_json,200)

    except Exception as e:
        logger.error(str(e))
        return response.error_response(str(e),None,400)


@router.get("/get_all_users")
def get_all_users(db: Session = Depends(get_db)):
    all_user = db.query(User).all()

    return_json = [user_auth_schema.GetUser.from_orm(user) for user in all_user]
    return response.success_response("user successfully registered",return_json,201)