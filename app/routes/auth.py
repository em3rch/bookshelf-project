from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user

from app.db_models import User
from app.extensions import db


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register_handler():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if not username or not email or not password:
            flash("All fields require to be filled with data.")
            return redirect(url_for("auth.register_handler"))
        
        if User.query.filter((User.username==username) | (User.email==email)).first():
            flash("User already exists.")
            return redirect(url_for("auth.register_handler"))
        
        user = User(
            username=username,
            email=email
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Account has been successfully created.")        

        return redirect(url_for("auth.login_handler"))


    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login_handler():
    if request.method == "POST":
        username_or_email = request.form.get("username_or_email")
        password = request.form.get("password")

        user = User.query.filter(
            (User.username==username_or_email) | (User.email==username_or_email)
        ).first()
        
        if not user:
            flash("Invalid username or email.")
            return redirect(url_for("auth.login_handler"))

        if not user.check_password(password):
            flash("Invalid password.")
            return redirect(url_for("auth.login_handler"))

        login_user(user)

        return redirect(url_for("main.index"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout_handler():
    logout_user()

    return redirect(url_for("main.index"))

