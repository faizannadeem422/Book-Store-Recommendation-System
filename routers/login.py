import random
import time
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

import auth
from mailer import send_plain_email
import models
import schema
from database import sessionLocal
from services import users as UsersService

router = APIRouter()

def get_db ():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]
    
# Create new user
@router.post("/register")
def register(register:schema.register, db:db_dependency, backgroundTasks:BackgroundTasks):
    
    otp = random.randint(100000, 999999)

    user_name = register.userName
    user_email = register.userEmail
    user_password = register.userPassword

    if UsersService.isUserExist(user_email, db):
        raise HTTPException(status_code=409, detail="User Already Exist!")

    user = UsersService.RegisterUser(
        username=user_name,
        email=user_email,
        plain_password=user_password,
        otp=otp,
        db=db
    )

    backgroundTasks.add_task(
        send_plain_email,
        receiver_email=user.user_email,
        subject="OTP Verification",
        body=f"OTP is {otp}"
    )
    
    return {
    "message": "User added successfully"
    }
 
# Verify OTP
@router.post("/verify")
def verifyOTP(verify:schema.verify, db:db_dependency):

    otp = verify.OTP
    email = verify.userEmail

    try:
        user = UsersService.GetUser(
            otp=otp,
            email=email,
            db=db
        )

        if not user.isVerified:
            user.isVerified = True
            user.OTP = 0
            user.otpExpiry = 0

            db.add(user)
            db.commit()
            db.refresh(user)
            return {"message":"Email verified successfully"}
        else:
            return {"message": "Invalid OTP"}
        
    except Exception as e:
        return {"message": "Invalid OTP"}

# Login a user 
@router.post("/login", response_model=schema.loginResponse)
def login(login:schema.login, db:db_dependency, backgroundTask:BackgroundTasks):
    email = login.userEmail
    userpassword = login.userPassword

    user = UsersService.GetUserForLogin(email, db)

    hashedpassword = user.user_password

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not auth.verify_password(userpassword, hashedpassword):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    user.auth_token = auth.create_access_token(
        data = {
            "userId": user.user_id,
            "userName": user.user_name,
            "userEmail": user.user_email,
        }
    )

    user.refresh_token = auth.create_access_token(
        data = {
            "userId": user.user_id,
            "userName": user.user_name,
            "userEmail": user.user_email,
        }
    )

    # Adding email task
    backgroundTask.add_task(
        send_plain_email,
        receiver_email=user.user_email,
        subject="Login Alert",
        body=f"A new device has been logged in"
    )

    return JSONResponse(
        content={
            "data": {
                "userID": user.user_id,
                "userName": user.user_name,
                "userEmail": user.user_email,
                "authToken": user.auth_token,
                "refreshToken": user.refresh_token
            }
        }, 
        status_code=200
    )
