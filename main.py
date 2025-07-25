import os
import time
from typing import Annotated
from fastapi import Depends, FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.background import BackgroundScheduler

import models
import routers.books
import routers.login
from database import engine, sessionLocal
import routers
from middleware.logger import LoggingMiddleware

from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Creates tables
models.Base.metadata.create_all(bind=engine)
scheduler = BackgroundScheduler()

logCounter = 0
def logCreator():
    global logCounter
    
    with open(f"./logs/{str(int(time.time()))}.txt", "w") as file:
        file.write(f"{time.time()}")
        file.close()
        logCounter += 1
        print("log added")

def logsDeleter():
    try:
        for fileName in os.listdir("./logs/"):
            filePath = os.path.join("./logs",fileName)
            os.remove(filePath)
        print("Files deleted successfully")
    except: 
        print("There might be a problem while removing files")

scheduler.add_job(logCreator, "interval", seconds=500)
scheduler.add_job(logsDeleter, "interval", seconds=1000)

scheduler.start()

def get_db ():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

app = FastAPI()

origins = ["*"]

templates = Jinja2Templates(directory="templates") # Templates directory

# Mount the 'static' folder
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(routers.login.router, prefix="/user", tags=["Users"])
app.include_router(routers.books.router, prefix="/books", tags=["Books"])

# Home route - Displays all books
@app.get("/")
def home(request: Request, db:db_dependency):
    booksData = []

    for book in db.query(models.books).all():
        booksData.append(
            {
                "bookID": book.book_id,
                "bookTitle": book.book_title,
                "bookAuthor": book.book_author,
                "bookPublisher": book.book_publisher,
                "bookPrice": book.book_price,
                "bookCategory": book.category
            }
        )

    return templates.TemplateResponse("home.html", {
        "request": request,
        "books": booksData
    })

@app.get("/file")
def file():
    return FileResponse("./static/imgs/me.jpg")