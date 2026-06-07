import os
from uuid import uuid4 # Universally Unique Identifier. Used to uniquely identify object , data, or files

from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import current_user, login_required


from werkzeug.utils import secure_filename

from app.db_models import Book
from app.extensions import db


books_bp = Blueprint("books", __name__)


@books_bp.route("/books")
@login_required
def books_list_handler():
    books = current_user.books

    return render_template("book_list.html", books=books)



@books_bp.route("/books/add", methods=["GET", "POST"])
@login_required
def book_add_handler():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        year = request.form.get("year", "").strip()
        genres = request.form.get("genres", "").strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "").strip()
        notes = request.form.get("notes", "").strip()
        cover = request.files.get("cover")

        cover_filename = None

        # Title verification
        if not title:
            flash("Book title is required.")
            return redirect(url_for("books.book_add_handler"))
        
        # Year verification
        try:
            year = int(year) if year else None
        except ValueError:
            flash("Year must be a number.")
            return redirect(url_for("books.book_add_handler"))

        # Status verification
        if status not in Book.BOOK_STATUSES:
            flash("Invalid status.")
            return redirect(url_for("books.book_add_handler"))
    
        # Cover verification
        if cover and cover.filename:
            extension = os.path.splitext(secure_filename(cover.filename))[1] # Get extension WITH the dot.

            if extension.lower().replace('.', '') not in Book.ALLOWED_COVER_EXTENSIONS:
                flash("Only PNG, JPG, JPED and WEBP files are allowed to be uploaded.")
                return redirect(url_for("books.book_add_handler"))

            cover_filename = f"{uuid4()}{extension}"

            upload_path = os.path.join(
                "app",
                "static",
                "uploads",
                "covers",
                cover_filename
            )

            cover.save(upload_path)
   
        book = Book(
            user_id=current_user.id,
            google_id=None,
            title=title,
            author=author or None,
            year=year,
            genres=genres or None,
            description=description or None,
            status=status,
            notes=notes or None,
            cover_url=None,
            cover_image=cover_filename
        )

        db.session.add(book)
        db.session.commit()

        flash("Book added successfully.")

        return redirect(url_for("books.books_list_handler"))

    return render_template("book_add.html")



@books_bp.route("/books/<int:book_id>")
@login_required
def book_details_handler(book_id: int):
    book = Book.query.get_or_404(book_id)

    if book.user_id != current_user.id:
        abort(403)

    return render_template(
        "book_details.html",
        book=book
    )


@books_bp.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
@login_required
def book_edit_handler(book_id: int):
    book = Book.query.get_or_404(book_id)

    if book.user_id != current_user.id:
        abort(403)


    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        year = request.form.get("year", "").strip()
        genres = request.form.get("genres", "").strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "").strip()
        notes = request.form.get("notes", "").strip()
        cover = request.files.get("cover")

        cover_filename = None

        # Title verification
        if not title:
            flash("Title is required.")
            return redirect(
                url_for("books.book_edit_handler", book_id=book.id)
            )

        try:
            year = int(year) if year else None
        except ValueError:
            flash("Year must be a number.")
            return redirect(
                url_for("books.book_edit_handler", book_id=book.id)
            )

        if status not in Book.BOOK_STATUSES:
            flash("Invalid status.")
            return redirect(
                url_for("books.book_edit_handler", book_id=book.id)
            )
        
        if cover and cover.filename:
            extension: str = os.path.splitext(secure_filename(cover.filename))[1]

            if extension.lower().replace('.', '') not in Book.ALLOWED_COVER_EXTENSIONS:
                flash("Only PNG, JPG, JPEG and WEBP are allowed.")
                return redirect(url_for("books.book_edit_handler", book_id=book.id))

            if book.cover_image:
                old_file = os.path.join(
                    "app",
                    "static",
                    "uploads",
                    "covers",
                    book.cover_image
                )

                if os.path.exists(old_file):
                    os.remove(old_file)

            cover_filename = f"{uuid4()}{extension}"

            upload_path = os.path.join(
                "app",
                "static",
                "uploads",
                "covers",
                cover_filename
            )

            cover.save(upload_path)
        
        book.title = title
        book.author = author or None
        book.year = year
        book.genres = genres or None
        book.description = description or None
        book.status = status
        book.notes = notes or None

        if cover_filename:
            book.cover_image = cover_filename

        db.session.commit()

        flash("Book updated successfully.")

        return redirect(url_for("books.book_details_handler", book_id=book.id))

    return render_template(
        "book_edit.html",
        book=book
    )


@books_bp.route("/books/<int:book_id>/delete", methods=["POST"])
@login_required
def book_delete_handler(book_id: int):
    book = Book.query.get_or_404(book_id)

    if book.user_id != current_user.id:
        abort(403)

    if book.cover_image:
        cover_path = os.path.join(
            "app",
            "static",
            "uploads",
            "covers",
            book.cover_image
        )

        if os.path.exists(cover_path):
            os.remove(cover_path)
        
    db.session.delete(book)
    db.session.commit()

    flash("Book has been removed from your bookshelf.")

    return redirect(url_for("books.books_list_handler"))
    
