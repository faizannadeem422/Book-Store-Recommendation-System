from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
import jwt
from sqlalchemy.orm import Session

import auth
from schemas import books as BookSchema
from database import sessionLocal
from services.books import AddBook, AddNewBookOpenFrequency, DeleteBook, FetchAllBooks, FetchAllBooksByUser, FetchBookOpenFrequency, FetchOneBook, UpdateBook, UpdateBookOpenFrequency
from services.recommendation import FetchBooks, GetTopCategories

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
def addNewBook(request:Request, book:BookSchema.addBook, db:db_dependency):
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

    # Adding new book using service function
    newBook = AddBook(
        userId = decodedToken["userId"],
        title = book.bookTitle,
        bookAuthor = book.bookAuthor,
        bookPublisher = book.bookPublisher,
        bookPrice = book.bookPrice,
        category = book.category,
        db=db
    )

    allBooks = FetchAllBooksByUser(userId=decodedToken["userId"], db=db)

    booksOpenFrequency = FetchBookOpenFrequency(category=book.category, db=db)

    if not booksOpenFrequency:
        AddNewBookOpenFrequency(book_id=newBook.book_id, category=book.category, db=db)

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

        # Decoding authorization token 
        decodedToken = auth.decode_access_token(authToken)
        if decodedToken == None:
            return JSONResponse(
                content={
                    "message": "Invalid Token",
                    "status_code": 401
                }
            )

        # Authorization Check
        if decodedToken == jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code= 401,
                detail="Unauthorized user"
            )
        
        # Token validation check
        if decodedToken == jwt.InvalidTokenError:
            raise HTTPException(
                status_code= 400,
                detail="Invalid token"
            )
        
        book = FetchOneBook(bookId=book_id, userId=decodedToken["userId"], db=db)

        isOpenFrequencyExists, OpenFrequency = FetchBookOpenFrequency(book.category, db)

        if isOpenFrequencyExists:
            UpdateBookOpenFrequency(category=book.category, db=db)

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

    books = FetchAllBooks(userId=decodedToken["userId"], db=db)
    return books

# Update a book
@router.put("/update")
def updateBook(request:Request, updateBook:BookSchema.updateBook, db:db_dependency):
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
    
    book = UpdateBook(
        userId=decodedToken["userId"],
        bookId=updateBook.bookID,
        updateBook=updateBook,
        db=db
    )

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

    if DeleteBook(userId=decodedToken["userId"], bookId=bookID, db=db):
        return JSONResponse(
            content={
                "message": "Book successfully deleted"
            },
            status_code=204
        )
    else:
        return JSONResponse(
            content={
                "message": "An error occured while deleting book"
            },
            status_code=400
        )

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
        frequencies = GetTopCategories(db)

        # topBooks = []

        for frequency in frequencies:
            topBooks = FetchBooks(category=frequency.category, db=db)
        
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
    