import datetime
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

import models
from database import sessionLocal

def get_db ():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

# This will fetch all books from Database
def FetchAllBooks(db:Session):
    booksData = []

    books = db.query(models.books).all()

    for book in books:
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

    return booksData
    

def AddBook(userId:int, title:str, bookAuthor:str, bookPublisher:str, bookPrice:int, category:str, db:Session):
    newBook = models.books(
        user_id = userId,
        book_title = title,
        book_author = bookAuthor,
        book_publisher = bookPublisher,
        book_price = bookPrice,
        category = category
    )

    db.add(newBook)
    db.commit()
    db.refresh(newBook)

    if newBook == None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return newBook

def FetchAllBooksByUser(userId:int, db: Session):
    allBooks = db.query(models.books).filter(
            models.books.user_id == userId
    ).all()

    if not allBooks:
        raise HTTPException(status_code=404, detail="Books not found!")

    return allBooks

def FetchBookOpenFrequency(category:str, db:Session):
    data = db.query(models.booksOpenFrequency).filter(
        models.booksOpenFrequency.category == category
    ).first()

    if data == None:
        return False

    return True, data

def AddNewBookOpenFrequency(book_id:int, category:str, db:Session):
    newBooksOpenFrequency = models.booksOpenFrequency(
        book_id = book_id,
        frequency = 0,
        category = category
    )

    db.add(newBooksOpenFrequency)
    db.commit()
    db.refresh(newBooksOpenFrequency)

    if newBooksOpenFrequency == None:
        raise HTTPException(status_code=404, detail="Books Frequency not added!")

    return newBooksOpenFrequency

def FetchOneBook(bookId:int, userId:int, db:Session):
    data = db.query(models.books).filter(
        ( models.books.book_id == bookId ) &
        ( models.books.user_id == userId )
    ).first()

    if data == None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    return data

def FetchAllBooks(userId:int, db:Session):
    data = db.query(models.books).filter(
        models.books.user_id == userId
    ).all()

    if data == None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    return data

def UpdateBookOpenFrequency(category:str, db:Session):
    data = db.query(models.booksOpenFrequency).filter(
        models.booksOpenFrequency.category == category
    ).first()

    if data == None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    data.frequency += 1
    data.open_timestamp = datetime.datetime.now()

    db.add(data)
    db.commit()
    db.refresh(data)

    return data

def UpdateBook(userId:int, bookId:int, updateBook, db:Session):
    book = db.query(models.books).filter(
        (models.books.user_id == userId ) &
        (models.books.book_id == bookId)
    ).first()

    if book == None:
        raise HTTPException(status_code=404, detail="Category not found")

    book.book_title = updateBook.bookTitle
    book.book_author = updateBook.bookAuthor
    book.book_publisher = updateBook.bookPublisher
    book.book_price = updateBook.bookPrice

    db.add(book)
    db.commit()
    db.refresh(book)

    return book

def DeleteBook(userId:int, bookId:int, db:Session):
    data = db.query(models.books).filter(
        (models.books.book_id == bookId) &
        (models.users.user_id == userId)
    ).first()

    if data == None:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(data)
    db.commit()

    return True

