from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relation, relationship
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True)
    password = db.Column(db.String(250))
    name = db.Column(db.String(250))

    #This will act like a List of BlogPost objects attached to each User. 
    #The "author" refers to the author property in the BlogPost class.
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)

    #Create Foreign Key, "users.id" the users refers to the tablename of User.
    author = relationship("User", back_populates="posts")
    # "users.id" the users refers to the tablename of User
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    posts = relationship("Comment", back_populates="comment_post")

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(250), nullable=False)

    comment_author = relationship("User", back_populates="comments")
    comment_author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    
    comment_post = relationship("BlogPost", back_populates="posts")
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
