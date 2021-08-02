from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_database.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(30))
    city = db.Column(db.String(30))

    #This will act like a List of BlogPost objects attached to each User. 
    #The "author" refers to the author property in the BlogPost class.
    books = relationship("Book", back_populates="owner")

class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)

    owner = relationship("User", back_populates="books")
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    title = db.Column(db.String(250), unique=True, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    release_date = db.Column(db.String(250), nullable=False)


db.create_all()