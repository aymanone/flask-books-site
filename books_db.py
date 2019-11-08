import csv
import os
from sqlalchemy import create_engine 
from sqlalchemy.orm import scoped_session,sessionmaker
engine = create_engine(os.getenv("DATABASE_URL"))
db=scoped_session(sessionmaker(bind=engine))
db.execute("DROP TABLE IF EXISTS Books;")

db.execute("CREATE TABLE IF NOT EXISTS Books ( isbn VARCHAR NOT NULL PRIMARY KEY , title VARCHAR NOT NULL,author VARCHAR NOT NULL , year VARCHAR NOT NULL);")
print("ayman make table")
file=open("books.csv")
reader=csv.reader(file)
next(reader)
for isbn,title,author,year in reader:
    
    db.execute("INSERT INTO Books (isbn,title,author,year) VALUES(:isbn,:title,:author,:year)",{"isbn":isbn,"title":title,"author":author,"year":year})
    
db.commit()
print("all values is inserted")
