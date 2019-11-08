import os
import requests
from flask import Flask, session,render_template,request,redirect,url_for,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
db.execute("CREATE TABLE IF NOT EXISTS Users( user_id SERIAL  PRIMARY KEY,user_name VARCHAR NOT NULL UNIQUE ,password VARCHAR NOT NULL);")
db.execute("CREATE TABLE IF NOT EXISTS Reviews(user_name VARCHAR NOT NULL,isbn VARCHAR NOT NULL,review VARCHAR NOT NULL, rating VARCHAR NOT NULL);")
db.commit()
api_key="kvM2zua6kslLqI6Hw3ZDRA"



@app.route("/")
def index():
    
    if session.get("user_name") is None:
        return render_template("index.html")
    return render_template("search.html")


@app.route("/sign_up",methods=["POST","GET"])
def sign_up():
    
    if request.method=="GET":
        
        return render_template("signup.html")
    mail=request.form.get("email")
    password=request.form.get("password")
    if db.execute('SELECT user_name FROM Users WHERE user_name = :username',
            {"username": mail}).rowcount > 0:
        
        
        
        return render_template("error.html",msg="name already there")
    try:
        
        db.execute("INSERT INTO Users (user_name,password)VALUES(:mail,:password)",{"mail":mail,"password":password})
        
    
        db.commit()
        
        
        session["user_name"]=mail
        
        return redirect(url_for('index'))
        
    except Exception as e:
        return str(e)
@app.route("/login",methods=["POST","GET"])
def login():
    
    if request.method=="POST":
        
        
        mail=request.form.get("email")
        
        password=request.form.get("password")
        if db.execute("SELECT user_name FROM Users WHERE user_name = :username AND password=:password", {"username": mail,"password":password}).rowcount>0:
            
            session["user_name"]=mail
            return redirect(url_for("search"))
            
            
            
        else:
            
            return render_template("error.html",msg="name or password is invalid")
    if session.get("user_name")!=None:
        
        
        return redirect(url_for("search"))
     
    return render_template("login.html")
        
    
@app.route("/search",methods=["GET","POST"])
def search():
    if session.get("user_name") is None:
        return render_template("error.html",msg="you are not loged in log or sign up first")
    
    if request.form.get("search"):
        search=request.form.get("search")
        return redirect(url_for('display', search=search))
    
    return render_template('search.html')
@app.route("/search/<string:search>")
def display(search):
    
    if session.get("user_name") is None:
        
        return render_template("error.html",msg="you are not loged in log or sign up first")
    result = db.execute('SELECT title, author, year, isbn FROM Books WHERE UPPER(title) LIKE UPPER(:search)\
            OR UPPER(author) LIKE UPPER(:search) OR UPPER(isbn) LIKE UPPER(:search)', {"search":'%'+search+'%'}).fetchall()
    return render_template("display.html",result=result)
@app.route("/books/<string:isbn>",methods=["GET","POST"])
def book_info(isbn):
    if session.get("user_name") is None:
        return render_template("error.html",msg="log first")
    #title, author, year, isbn = request.args.get("title"), request.args.get("author"), request.args.get("year"), request.args.get("isbn")
    book=db.execute("SELECT title,author,year FROM Books WHERE isbn=:isbn",{"isbn":isbn}).fetchall()
    if len(book)==0:
        return render_emplate("error.html",msg="no such book in our site")
    title=book[0]["title"]
    year=book[0]["year"]
    #isbn=book["isbn"]
    author=book[0]["author"]
    #reviews=request.args.get(reviews)
           
    if title is None  or author is None or isbn is None:
        
           
           
        return render_template("error.html",msg="there are missing parameter please follow the book link")
    
    
    msg=""
    if request.method=="POST":
        if db.execute("SELECT user_name FROM Reviews where user_name=:user and isbn=:isbn",{"user":session.get("user_name"),"isbn":isbn}).rowcount>0:
            #return render_template("error.html",msg="you reviewd this before")
            msg="you reviewed this before"
        
        else:
            msg="you jsut review this now"
            review=request.form.get("review")
            rate=request.form.get("rate")
            new_review=[review,rate]
        #reviews.append(new_review)
        #reviews=[1,2,3]
        
            db.execute("INSERT INTO Reviews (user_name,isbn,review,rating) VALUES(:user,:isbn,:rev,:rate)",{"user":session.get("user_name"),"isbn":isbn,"rev":review,"rate" : rate })
            db.commit()
        
           
           
    reviews=db.execute("SELECT review,rating FROM Reviews where isbn=:isbn",{"isbn":isbn}).fetchall()
    res=requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": api_key, "isbns": isbn})
    try:
        res=res.json()
        avg=res["books"][0]['average_rating']
        work_rev=res["books"][0]['work_reviews_count']
        
    except :
        avg=""
        work_rev=""
    return render_template("bookinfo.html",title=title,author=author,year=year,isbn=isbn,reviews=reviews,msg=msg,work_rev=work_rev,avg=avg)



        


@app.route("/logout")
def logout():
    if session.get("user_name") != None:
        
        del session["user_name"]
    return render_template("index.html")
@app.route("/api/<string:isbn>",methods=["GET"])
def api(isbn):
    book=db.execute("SELECT title,author,year FROM Books WHERE  isbn=:isbn",{"isbn":isbn}).fetchone()
    if book==None:
        return jsonify({"error":"not valid isbn"}),404
    info={}
    info["isbn"]=str(isbn)
    info["title"]=book["title"]
    info["year"]=book["year"]
    info["author"]=book["author"]
    res=requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": api_key, "isbns": isbn})
    try:
        
        res=res.json()
        info["average_score"]=res["books"][0]['average_rating']
        info["review_count"]=res["books"][0]['work_reviews_count']
    except:
        info["average_score"]="Not Recognize"
        info["review_count"]="Not Recognize"
    return jsonify(info)
    
    
    
