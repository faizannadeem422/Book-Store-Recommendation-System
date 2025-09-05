import datetime
from random import random
from time import time
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

import auth
import models
from database import sessionLocal

# Register a new user in database
def RegisterUser(username:str, email:str, plain_password:str, otp:int, db:Session):
    
    future_time = datetime.datetime.now() + datetime.timedelta(minutes=10)

    user = models.users(
        user_name = username,
        user_email = email,
        user_password = auth.get_password_hash(plain_password),
        created_at = datetime.datetime.now(),
        isVerified = False,
        OTP = otp,
        otpExpiry = int(future_time.timestamp())
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

# Check if the user exists or not
def isUserExist(email:str, db:Session):
    user = db.query(models.users).filter(models.users.user_email == email).first()

    if user != None:
        return True
    else: 
        return False

# Get a user from database 
def GetUser(otp:int, email:str, db:Session):
    user = db.query(models.users).filter(
        (models.users.OTP == otp) & 
        (models.users.user_email == email) &
        (models.users.otpExpiry >= int(time()))
    ).first()   

    if user == None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

def GetUserForLogin(email:str, db: Session):
    user = db.query(models.users).filter(
        models.users.user_email == email
    ).first()
    
    if user == None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user