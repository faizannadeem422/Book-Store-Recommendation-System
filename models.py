from database import Base
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean


class users(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(100), unique=False, nullable=False)
    user_email = Column(String(120), unique=True, nullable=False)
    user_password = Column(String(200), nullable=False)
    isVerified = Column(Boolean, nullable=True)
    OTP = Column(Integer, nullable=True, unique=False)
    otpExpiry = Column(Integer, nullable=True, unique=False)
    auth_token = Column(String(1000), nullable=True)
    refresh_token = Column(String(1000), nullable=True)
    created_at = Column(DateTime, nullable=True)


class books(Base):
    __tablename__ = "books"

    book_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(users.user_id))
    book_title = Column(String(200), unique=False, nullable=False)
    book_author = Column(String(200), unique=False, nullable=True)
    book_publisher = Column(String(200), unique=False, nullable=True)
    book_price = Column(Integer, unique=False, nullable=False)
    category = Column(String, unique=False, nullable=False)

    def __repr__(self):
        return f"Book ID: {self.book_id}, Title: {self.book_title}, Author: {self.book_author}, Publisher: {self.book_publisher}, Price: {self.book_price}"

class booksOpenFrequency(Base):
    __tablename__ = "books_open_frequency"

    booksOpenFrequency_id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey(books.book_id))
    frequency = Column(Integer, nullable=False)
    category = Column(String, nullable=False)    