import os
import smtplib
import dotenv
from operator import pos
from datetime import date
from functools import wraps

from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import login_manager, login_user, LoginManager, login_required, current_user, logout_user
from flask_gravatar import Gravatar
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, BlogPost, Comment
from forms import ContactForm, CreatePostForm, RegisterForm, LoginForm, CommentForm

dotenv.load_dotenv()

MAIL_SERVER_PASSWORD = os.environ.get("MAIL_SERVER_PASSWORD")
MAIL_ADDRESS = os.environ.get("MAIL_ADDRESS")
RECIPIENT_MAIL = os.environ.get("RECIPIENT_MAIL")

print(MAIL_ADDRESS, MAIL_SERVER_PASSWORD)

app = Flask(__name__)

app.config['SECRET_KEY'] = "mysecret7777"
# app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
# second argument is used if a file is run locally - no DATABASE_URL key in environment
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///blog.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
ckeditor = CKEditor(app)
Bootstrap(app)

gravatar = Gravatar(app,
                    size=200,
                    rating='g',
                    default='identicon',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

login_manager = LoginManager()
login_manager.init_app(app)

def admin_only(f):
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
                flash("You have successfully logged in")
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


@app.route("/contact", methods=["GET", "POST"])
def contact():
    contact_form = ContactForm()
    if contact_form.validate_on_submit():
        subject = f"Subject:Mail from:{contact_form.name.data} regarding ......\n\n"
        text = f"{contact_form.message.data}"
        message = subject + text
        with smtplib.SMTP('smtp.mail.yahoo.com') as connection:
            connection.starttls()
            connection.login(MAIL_ADDRESS, MAIL_SERVER_PASSWORD)
            connection.sendmail(MAIL_ADDRESS, RECIPIENT_MAIL, msg=message.encode("utf-8"))
        return redirect(url_for("contact"))
    else:
        return render_template("contact.html", contact_form=contact_form)
        

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
