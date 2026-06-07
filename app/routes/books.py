from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required



books_bp = Blueprint("books", __name__)


@books_bp.route("/books-list")
@login_required
def books_list_handler():
    books = current_user.books

    return render_template("book_list.html", books=books)



@books_bp.route("/book-creation", methods=["GET", "POST"])
@login_required
def book_creation_handler():
    return render_template("book_creation.html")
