from pydantic import BaseModel, EmailStr



class RegisterUser(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    address: str
    phone_number: str
    city: str
    state: str
    country_name: str

    class Config:
        orm_mode = True
        from_attributes=True

class LoginUserInput(BaseModel):
    email: EmailStr
    password: str

    class Config:
        orm_mode = True
        from_attributes=True


class ForgetPass1Input(BaseModel):
    email: EmailStr

    class Config:
        orm_mode = True
        from_attributes=True

class ForgetPass2Input(BaseModel):
    email: EmailStr
    otp: str
    password: str

    class Config:
        orm_mode = True
        from_attributes=True

class GetUser(BaseModel):
    user_id: int
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    address: str
    phone_number: str
    city: str
    state: str
    country_name: str

    class Config:
        orm_mode = True
        from_attributes=True