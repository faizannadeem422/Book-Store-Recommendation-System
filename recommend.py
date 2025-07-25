from sqlalchemy.orm import Session

import database
import models

def get_db():
    db = database.sessionLocal()
    try:
        yield db
    finally:
        db.close()


def recommend ():
    db:Session
    booksFrequency = db.query(models.booksOpenFrequency).all()

    print(booksFrequency)


recommend()