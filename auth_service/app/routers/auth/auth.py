from fastapi import APIRouter, Depends, BackgroundTasks
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
from email.message import EmailMessage
import aiosmtplib
from random import randint


SECRET_KEY= os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

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

async def send_email(subject: str, recipient: str, body: str):
    message = EmailMessage()
    message["From"] = EMAIL_USERNAME
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname=EMAIL_HOST,
        port=EMAIL_PORT,
        username=EMAIL_USERNAME,
        password=EMAIL_PASSWORD,
        start_tls=True
    )

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
        
        if db_user.otp_verified == 0 or db_user.otp_verified == "0":
            logger.error(f"This user otp is not verified yet.")
            return response.error_response("This user otp is not verified yet.",None,400)
        
        if not verify_password(user_input.password + os.getenv("SECRET_KEY"), db_user.password):
            logger.error(f"Login failed: wrong password for {user_input.email}")
            return response.error_response(f"Login failed: wrong password for {user_input.email}",None,400)
        
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

@router.post("/generate_otp")
def forget_password_step1(user_input: user_auth_schema.ForgetPass1Input, background_tasks: BackgroundTasks,db: Session = Depends(get_db)):
    try:
        find_user = db.query(User).filter(User.email == user_input.email).first()

        if not find_user:
            logger.error(f"no user found using this email")
            return response.error_response("no user found using this email","no user found using this email",400)

        otp = randint(11111,99999)
        email_body = f"your otp is {otp}"

        find_user.otp = otp
        find_user.otp_verified = "0"
        db.commit()
        db.refresh(find_user)

        background_tasks.add_task(send_email, "OTP from realhub.ai", user_input.email, email_body)

        return response.success_response(f"otp successfully sent to: {user_input.email}",{},201)
    except Exception as e:
        return response.error_response(str(e),str(e),400)
    
@router.post("/submit_otp")
def forget_password_step2(user_input: user_auth_schema.ForgetPass2Input, background_tasks: BackgroundTasks,db: Session = Depends(get_db)):
    try:
        find_user = db.query(User).filter(User.email == user_input.email).first()

        if not find_user:
            logger.error(f"no user found using this email")
            return response.error_response("no user found using this email","no user found using this email",400)

        otp = user_input.otp
        hashed_pw = hash_password(user_input.password)

        if int(find_user.otp) != int(otp):
            logger.error(f"otp is not valid try again")
            return response.error_response("otp is not valid try again","otp is not valid try again",400)

        find_user.password = hashed_pw
        find_user.otp_verified = "1"
        db.commit()
        db.refresh(find_user)

        return response.success_response(f"password changed successfully.",{},201)
    except Exception as e:
        return response.error_response(str(e),str(e),400)