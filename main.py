from typing import Annotated
from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.background import BackgroundScheduler

import models
import routers.books
import routers.login
from database import engine, sessionLocal
import routers
from middleware.logger import LoggingMiddleware
from backgroundTasks import tasks

from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Creates tables
models.Base.metadata.create_all(bind=engine)
scheduler = BackgroundScheduler()

scheduler.add_job(tasks.logCreator, "interval", seconds=5)
scheduler.add_job(tasks.logsDeleter, "interval", seconds=60)

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

@app.get("/addbookpage")
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

    return templates.TemplateResponse("addBook.html", {
        "request": request,
        "books": booksData
    })

@app.get("/updatebookpage")
def home(request: Request, db:db_dependency, bookID:int | None = None):
    return templates.TemplateResponse("updatebook.html", {
        "request": request,
        "bookID": bookID
    })

@app.get("/version")
def file():
    import sys
    return {
        "versionData": str(sys.version)
    }
