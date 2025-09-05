from fastapi import HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

import models

def GetTopCategories(db:Session):
    data = db.query(models.booksOpenFrequency).order_by(
            desc(models.booksOpenFrequency.frequency)
        ).limit(3).all()

    if not data:
        raise HTTPException(
            status_code=404,
            detail="Top Books Not Found"
        )
    
    return data

def FetchBooks(category:str, db:Session):
    data = db.query(models.books).filter(
        models.books.category == category
    ).all()

    if data == None:
        raise HTTPException(
            status_code=404,
            detail="Books Not Found"
        )
    
    return data