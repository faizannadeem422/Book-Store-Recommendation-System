from pydantic import BaseModel, constr, EmailStr, field_validator, validator

class user(BaseModel):
    userID:int
    userName:str
    userEmail:EmailStr

class register(BaseModel):
    userName: str = constr(min_length=8)
    userEmail: EmailStr
    userPassword: str = constr(min_length=8)

    @field_validator('userPassword')
    def validate_password(cls, v):
        import re
        if not re.search(r'[A-Za-z]', v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r'\d', v):
            raise ValueError("Password must contain at least one number")
        return v

class verify(BaseModel):
    userEmail:str
    OTP:int

class login(BaseModel):
    userEmail: str
    userPassword: str

class loginResponse(BaseModel):
    userID: int
    userName: str
    userEmail: str
    authToken: str
    refreshToken: str