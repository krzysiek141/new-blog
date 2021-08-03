# we flasku można normalnie stosować obsługę błędów mimo że nie są one wyrzucane na zewnątrz przez debugger

from operator import pos
from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relation, relationship
from flask_login import UserMixin, login_manager, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from flask_gravatar import Gravatar
from functools import wraps
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
# second argument is used if a file is run locally
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL2", "sqlite:///blog.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

def admin_only(f):
    # In a nutshell, it helps prevent decorators from masking identity of the
    # decorated functions. Thus, the functions can keep their metadata even
    # after they are decorated by decorators.
    @wraps(f)
    def wrapper_function(*args, **kwargs):
        if current_user.is_authenticated:
            if current_user.id != 1:
                return abort(403)
            else:
                return f(*args, *kwargs)
        else:
            return abort(403)
    return wrapper_function

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

##CONFIGURE TABLES

# When creating a relation between the two tables, there is a hidden author
# column which is created automatically in the Post class. This was the backref
# that was added while creating the model. Angela is tapping into that author
# column to retrieve the name. This is how I've created the new post,
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

    comment_author = relationship("User", back_populates="comments")
    comment_author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    
    comment_post = relationship("BlogPost", back_populates="posts")
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))

db.create_all()

gravatar = Gravatar(app,
                    size=200,
                    rating='g',
                    default='identicon',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route('/register', methods=["GET", "POST"])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        # user already in database
        if User.query.filter_by(email=register_form.email.data).first():
            flash("You have already signed up with this email. Log in instead.")
            return redirect(url_for('login'))
        else:
            # no such user in database
            hashed_and_salted_password = generate_password_hash(
                register_form.password.data,
                'pbkdf2:sha256',
                8 
            )
            new_user = User(
                email=register_form.email.data,
                password=hashed_and_salted_password,
                name=register_form.name.data
                )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("get_all_posts"))
    else:
        return render_template("register.html", form=register_form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        found_user = User.query.filter_by(email=form.email.data).first()
        if found_user:
            if check_password_hash(found_user.password, form.password.data):
                login_user(found_user)
                return redirect(url_for('get_all_posts'))
            else:
                flash("The password is incorrect. Try again")
                return redirect(url_for('login'))
        else:
            flash("Specified email doesn't exist in the database. Try again.")
            return redirect(url_for('login'))
    else:
        return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    form = CommentForm()
    requested_post = BlogPost.query.get(post_id)
    if form.validate_on_submit():
        if current_user.is_authenticated:
            new_comment = Comment(
                text=form.comment.data,
                comment_author_id = current_user.id,
                post_id=post_id
            )
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for("show_post", post_id=post_id))
        else:
            flash("You have to be logged in to leave a comment")
            return redirect(url_for("login"))
    else:
        return render_template("post.html", post=requested_post, form=form)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")



@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form)



@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run()
