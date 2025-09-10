from pydantic import BaseModel 

class addBook(BaseModel):
    bookTitle: str
    bookAuthor: str
    bookPublisher: str
    bookPrice: int = 200
    category: str

class updateBook(BaseModel):
    bookID: int
    bookTitle: str
    bookAuthor: str
    bookPublisher: str
    bookPrice: int