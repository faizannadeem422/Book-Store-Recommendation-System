from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
import jwt
from sqlalchemy import desc
from sqlalchemy.orm import Session
import auth
import models
import schema
from database import sessionLocal
import utils

router = APIRouter()

def get_db ():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]

# Add a book
@router.post("/add")
def addNewBook(request:Request, book:schema.addBook, db:db_dependency):
    authToken = request.headers.get("Authorization")

    # current_user: schema.user = Depends(utils.get_current_user)
    # print(current_user.userId)


    decodedToken = auth.decode_access_token(authToken)

    if decodedToken == None:
        return JSONResponse(
            content={
                "message": "Invalid Token",
                "status_code": 401
            }
        )

    if decodedToken == jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code= 401,
            detail="Unauthorized user"
        )
    
    if decodedToken == jwt.InvalidTokenError:
        raise HTTPException(
            status_code= 400,
            detail="Invalid token"
        )

    newBook = models.books(
        user_id = decodedToken["userId"],
        book_title = book.bookTitle,
        book_author = book.bookAuthor,
        book_publisher = book.bookPublisher,
        book_price = book.bookPrice,
        category = book.category
    )

    db.add(newBook)
    db.commit()
    db.refresh(newBook)

    allBooks = db.query(models.books).filter(
        models.users.user_id == decodedToken["userId"]
    ).all()

    booksOpenFrequency = db.query(models.booksOpenFrequency).filter(
        models.booksOpenFrequency.category == newBook.category
    ).first()

    if not booksOpenFrequency or booksOpenFrequency.category != newBook.category:
        newBooksOpenFrequency = models.booksOpenFrequency(
            book_id = newBook.book_id,
            frequency = 0,
            category = newBook.category
        )

        db.add(newBooksOpenFrequency)
        db.commit()
        db.refresh(newBooksOpenFrequency)

    data = []
    for book in allBooks:
        data.append(
            {
                "bookID": book.book_id,
                "bookTitle": book.book_title,
                "bookAuthor": book.book_author,
                "bookPublisher": book.book_publisher,
                "bookPrice": book.book_price,
                "bookCategory": book.category
            }
        )
        
    return {
        "message": "Book added successfully",
        "Books": data
    }

# Get a single book - Query Parameter
@router.get("/id")
def getBook(request:Request, book_id:int, db:db_dependency):
    try:
        authToken = request.headers.get("Authorization")

        decodedToken = auth.decode_access_token(authToken)
        if decodedToken == None:
            return JSONResponse(
                content={
                    "message": "Invalid Token",
                    "status_code": 401
                }
            )

        if decodedToken == jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code= 401,
                detail="Unauthorized user"
            )
        
        if decodedToken == jwt.InvalidTokenError:
            raise HTTPException(
                status_code= 400,
                detail="Invalid token"
            )
        print(decodedToken)
        
        book = db.query(models.books).filter(
            (models.books.book_id == book_id) &
            (models.books.user_id == decodedToken["userId"])
        ).first()
        
        if book == None:
            
            raise HTTPException(
                status_code=404,
                detail="Book not found"
            )
        
        openFrequency = db.query(models.booksOpenFrequency).filter(
            models.booksOpenFrequency.category == book.category
        ).first()

        if openFrequency:
            openFrequency.frequency += 1
            openFrequency.open_timestamp = datetime.now()

            db.add(openFrequency)
            db.commit()
            db.refresh(openFrequency)

        return {
            "bookID": book.book_id,
            "bookTitle": book.book_title,
            "bookAuthor": book.book_author,
            "bookPublisher": book.book_publisher,
            "bookPrice": book.book_price,
            "bookCategory": book.category
        }
    except Exception as e:
        print(f"Error at getBooks() is: {e}")

# Get all books
@router.get("/all")
def getAllBooks(request:Request, db:db_dependency):
    authToken = request.headers.get("Authorization")

    decodedToken = auth.decode_access_token(token=authToken)

    if decodedToken == None:
        return JSONResponse(
            content={
                "message": "Invalid Token",
                "status_code": 401
            }
        )

    if decodedToken == jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code= 401,
            detail="Unauthorized user"
        )
    
    if decodedToken == jwt.InvalidTokenError:
        raise HTTPException(
            status_code= 400,
            detail="Invalid token"
        )

    books = db.query(models.books).filter(
        models.books.user_id == decodedToken["userId"]
    ).all()

    return books

# Update a book
@router.put("/update")
def updateBook(request:Request, updateBook:schema.updateBook, db:db_dependency):
    authToken = request.headers.get("Authorization")

    decodedToken = auth.decode_access_token(token=authToken)

    if decodedToken == None:
        return JSONResponse(
            content={
                "message": "Invalid Token",
                "status_code": 401
            }
        )

    print("debug")

    if decodedToken == jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code= 401,
            detail="Unauthorized user"
        )
    
    if decodedToken == jwt.InvalidTokenError:
        raise HTTPException(
            status_code= 400,
            detail="Invalid token"
        )
    
    book = db.query(models.books).filter(
        (models.books.user_id == decodedToken["userId"]) &
        (models.books.book_id == updateBook.bookID)
    ).first()

    print(book)

    book.book_title = updateBook.bookTitle
    book.book_author = updateBook.bookAuthor
    book.book_publisher = updateBook.bookPublisher
    book.book_price = updateBook.bookPrice

    db.add(book)
    db.commit()
    # db.refresh(book)

    return JSONResponse(
        content={  
            "message": "Book added successfully",     
            "UpdatedBook": {
            "bookID": book.book_id,
            "BookTitle": book.book_title,
            "BookAuthor": book.book_author,
            "BookPublisher": book.book_publisher,
            "BookPrice": book.book_price,
            "Category": book.category
            }
        }, 
        status_code=200
    )

# Delete a book - Path Parameter
@router.delete("/delete/{bookID}")
def delete(bookID:int, request:Request, db:db_dependency, limit:int = 10):
    authToken = request.headers.get("Authorization")

    decodedToken = auth.decode_access_token(token=authToken)

    if decodedToken == None:
        return JSONResponse(
            content={
                "message": "Invalid Token",
                "status_code": 401
            }
        )

    if decodedToken == None:
        return JSONResponse(
            content={
                "message": "Invalid Token",
                "status_code": 401
            }
        )

    if decodedToken == jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code= 401,
            detail="Unauthorized user"
        )
    
    if decodedToken == jwt.InvalidTokenError:
        raise HTTPException(
            status_code= 400,
            detail="Invalid token"
        )

    book = db.query(models.books).filter(
        (models.books.book_id == bookID) &
        (models.users.user_id == decodedToken["userId"])
    ).first()

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    db.delete(book)
    db.commit()

    return {
        "message": "Book successfully deleted"
    }

# Recommended Books
@router.get("/recommendations")
def recommendations(request:Request, db:db_dependency):
    authToken = request.headers.get("Authorization")

    decodedToken = auth.decode_access_token(token=authToken)

    if decodedToken == None:
        return JSONResponse(
            content={
                "message": "Invalid Token",
                "status_code": 401
            }
        )

    if decodedToken == jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code= 401,
            detail="Unauthorized user"
        )
    
    if decodedToken == jwt.InvalidTokenError:
        raise HTTPException(
            status_code= 400,
            detail="Invalid token"
        )

    try:
        frequencies = db.query(models.booksOpenFrequency).order_by(
            desc(models.booksOpenFrequency.frequency)
        ).limit(3).all()

        # topBooks = []

        for frequency in frequencies:
            topBooks = db.query(models.books).filter(frequency.category == models.books.category).all()
        
        data = []

        for book in topBooks:
            data.append(
                {
                    "bookID": book.book_id,
                    "bookTitle": book.book_title,
                    "bookAuthor": book.book_author,
                    "bookPublisher": book.book_publisher,
                    "bookPrice": book.book_price,
                    "bookCategory": book.category
                }
            )
        return JSONResponse(content=data, status_code=200)
    except Exception as e:
        print(f"An error occurred while fetching popular books: {e}")
        return []
    