from flask import render_template, Blueprint, request, flash, abort, session, redirect, url_for
from flask_login import current_user

from app.services.google_books import search_books, LANGUAGES, get_book
from app.db_models import Book


main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET"])
def index():
    query = request.args.get("q", "").strip()
    lang = request.args.get("lang", "").strip()

    results = []

    if lang not in LANGUAGES:
        lang = ""

    if query:
        session["query"] = query

        try:
            results = search_books(query, lang)

            if not results:
                flash("No were book were found. Try a different query or change the language filter.")
        except Exception as err:
            flash("Google Books API is currently unavailable. Please try again later.")
            print(err)

    if session.get("query"):
        query=session.get("query")

    return render_template(
        "index.html",
        results=results,
        query=query,
        lang=lang,
        languages=LANGUAGES
    )


@main_bp.route("/search/<string:google_id>")
def search_details_handler(google_id):
    try:
        book = get_book(google_id)
    except Exception as err:
        flash("Could not fetch book details. Pleasy try again later.")
        print(err)
        return redirect(url_for("main.index"))

    if book is None:
        abort(404)

    # Check if it is already on user's shelf 
    on_shelf = False
    if current_user.is_authenticated:
        # db.Model.query.filter_by returns either found model object or None
        on_shelf = Book.query.filter_by(
            user_id=current_user.id,
            google_id=google_id
        ).first() is not None # So, it returns True is there is something that has been returned by query.filter_by method

        
    return render_template(
        "search_details.html",
        book=book,
        on_shelf=on_shelf
    )



@main_bp.route("/about")
def about():
    return render_template("about.html")




