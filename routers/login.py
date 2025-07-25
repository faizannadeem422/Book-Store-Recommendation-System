from datetime import datetime, timedelta
import random
import time
from typing import Annotated
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import auth
from mailer import send_plain_email
import models
import schema
from database import sessionLocal

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
    try:
        otp = random.randint(100000, 999999)
        future_time = datetime.now() + timedelta(minutes=10)

        user = models.users(
            user_name = register.userName,
            user_email = register.userEmail,
            user_password = auth.get_password_hash(register.userPassword),
            created_at = datetime.now(),
            isVerified = False,
            OTP = otp,
            otpExpiry = int(future_time.timestamp())
        )


        db.add(user)
        db.commit()
        db.refresh(user)

        backgroundTasks.add_task(
            send_plain_email,
            receiver_email=user.user_email,
            subject="OTP Verification",
            body=f"OTP is {otp}"
        )
        

        return {
        "message": "User added successfully"
        }

    except Exception as e:
        return {
            "error": e
        }
    
# Verify OTP
@router.post("/verify")
def verifyOTP(verify:schema.verify, db:db_dependency):
    try:
        user = db.query(models.users).filter(
            (models.users.OTP == verify.OTP) & 
            (models.users.user_email == verify.userEmail) &
            (models.users.otpExpiry < int(time.time()))
        ).first()   

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

# Login a user - JSONResponse & Pydantic Output Validation
@router.post("/login", response_model=schema.loginResponse)
def login(login:schema.login, db:db_dependency, backgroundTask:BackgroundTasks):
    user = db.query(models.users).filter(
        login.userEmail == models.users.user_email
    ).first()

    userpassword = login.userPassword

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

    db.commit()
    db.refresh(user)

    # Adding email task
    backgroundTask.add_task(
        send_plain_email,
        receiver_email="imfaizannadeem2@gmail.com",
        subject="Login Alert",
        body=f"A new device has been logged in"
    )

    return JSONResponse(
        content={
            "message": "Login successful",
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
