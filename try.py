import csv
import os
from sqlalchemy import create_engine 
from sqlalchemy.orm import scoped_session,sessionmaker
engine = create_engine(os.getenv("DATABASE_URL"))
db=scoped_session(sessionmaker(bind=engine))
user="eee@ee.com"
search="q"
result=db.execute('SELECT title, author, year, isbn FROM Books WHERE UPPER(title) LIKE UPPER(:search)\
            OR UPPER(author) LIKE UPPER(:search) OR UPPER(isbn) LIKE UPPER(:search)', {"search":'%'+search+'%'}).fetchall()
result=db.execute("SELECT user_name,isbn FROM Reviews WHERE isbn=:isbn",{"isbn":"-1"})
row=result.fetchall()

print(len(row))
#print(row[0])

