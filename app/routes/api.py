from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user, login_user, logout_user

from app.db_models import Book, User
from app.extensions import db

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


def book_to_dict(book: Book) -> dict:
    return {
        "id": book.id,
        "google_id": book.google_id,
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "genres": book.genres,
        "description": book.description,
        "cover_url": book.cover_url,
        "cover_image": book.cover_image,
        "status": book.status,
        "notes": book.notes,
        "added_at": book.added_at,
        "updated_at": book.updated_at
    }


# POST /api/v1/auth/register
@api_bp.route("/auth/register", methods=["POST"])
def api_register_handler():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Request body must be valid JSON."
        }), 400

    username = str(data.get("username", "")).strip()
    email    = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", "")).strip()

    if not username or not email or not password:
        return jsonify({
            "error": "Fields 'username', 'email' and 'password' are required."
        }), 400

    if len(password) < 6:
        return jsonify({
            "error": "Password must be at least 6 characters long."
        }), 400
    
    if User.query.filter(
        (User.username == username) | (User.email == email)
    ).first():
        return jsonify({
            "error": "Username or email is already taken."
        }), 409
    
    user = User(username=username, email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "Account created successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }), 201


# POST /api/v1/auth/login
@api_bp.route("/auth/login", methods=["POST"])
def api_login_handler():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Request body must be valid JSON."
        }), 400

    username_or_email = str(data.get("username_or_email", "")).strip()
    password = str(data.get("password", "")).strip()

    if not username_or_email or not password:
        return jsonify({
            "error": "Fields 'username_or_email' and 'password' are required."
        }), 400

    user = User.query.filter(
        (User.username == username_or_email) | (User.email == username_or_email)
    ).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials."}), 401

    login_user(user)

    return jsonify({
        "message": "Logged in successfully.",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
    }), 200

# POST /api/v1/auth/logout
@api_bp.route("/auth/logout", methods=["POST"])
@login_required
def api_logout():
    logout_user()
    return jsonify({"message": "Logged out successfully."}), 200


# GET /api/v1/books
@api_bp.route("/books", methods=["GET"])
@login_required
def api_books_list_handler():
    status = request.args.get("status", "").strip()


    if status and status not in Book.BOOK_STATUSES:
        return jsonify({
            "error": f"Invalid status. Allowed values: {', '.join(Book.BOOK_STATUSES)}."
        }), 400


    query = Book.query.filter_by(user_id=current_user.id)

    if status:
        query = query.filter_by(status=status)

    books = query.order_by(Book.added_at.desc()).all()

    return jsonify({
        "total": len(books),
        "books": [book_to_dict(b) for b in books]
    }), 200



# GET /api/v1/books/<id>
@api_bp.route("/books/<int:book_id>", methods=["GET"])
@login_required
def api_book_details_handler(book_id: int):
    book = Book.query.get_or_404(book_id)

    if book.user_id != current_user.id:
        return jsonify({
            "error": "Access forbidden."
        }), 403

    return jsonify(book_to_dict(book)), 200
    

# POST /api/v1/books
@api_bp.route("/books", methods=["POST"])
@login_required
def api_book_create_handler():
    data = request.get_json(silent=True) # Do not raise an error if there was some poor-quality JSON (without some syntax components)

    if not data:
        return jsonify({
            "error": "Request body must be valid JSON."
        }), 400
    
    title = data.get("title").strip() if data.get("title") else ""

    if not title:
        return jsonify({
            "error": "Field 'title' is required."
        }), 400

    status = data.get("status", "wanted")
    if status and status not in Book.BOOK_STATUSES:
        return jsonify({
            "error": f"Invalid status. Allowed statuses: {', '.join(Book.BOOK_STATUSES)}."
        }), 400

    year = data.get("year")
    if year is not None:
        if not isinstance(year, int) or year < 0 or year > 9999:
            return jsonify({
                "error": "Field 'year' must be an integer between 0 and 9999."
            }), 400

    book = Book(
        user_id=current_user.id,
        google_id=None,
        title=title,
        author=data.get("author") or None,
        year=year,
        genres=data.get("genres") or None,
        description=data.get("description") or None,
        cover_url=data.get("cover_url") or None,
        cover_image=None,
        status=status,
        notes=data.get("notes") or None
    )

    db.session.add(book)
    db.session.commit()

    return jsonify(book_to_dict(book)), 201


# PATCH /api/v1/books/<id>
@api_bp.route("/books/<int:book_id>", methods=["PATCH"])
@login_required
def api_book_update_handler(book_id: int):
    book = Book.query.get_or_404(book_id)

    if book.user_id != current_user.id:
        return jsonify({
            "error": "Access forbidden."
        }), 403

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Request body must be valid JSON."
        }), 400

    UPDATABLE_FIELDS = (
        "title",
        "author",
        "year",
        "genres",
        "description",
        "notes",
        "status"
    )

    unknown = [k for k in data if k not in UPDATABLE_FIELDS]
    if unknown:
        return jsonify({
            "error": f"Unknown field(s): {', '.join(unknown)}.\n"
            f"Updatable fields: {', '.join(UPDATABLE_FIELDS)}."
        }), 400

    
    if "title" in data:
        title = str(data.get("title").strip()) if data.get("title") else ""

        if not title:
            return jsonify({
                "error": "Field 'title' cannot be empty"
            }), 400

        book.title = title
    
    if "author" in data:
        book.author = str(data.get("author").strip()) or None

    if "year" in data:
        year = data.get("year")
        if year is not None:
            if not isinstance(year, int) or year < 0 or year > 9999:
                return jsonify({"error": "Field 'year' must be an integer between 0 and 9999."}), 400

        book.year = year

    if "genres" in data:
        book.genres = str(data["genres"]).strip() or None

    if "description" in data:
        book.description = str(data["description"].strip()) or None

    if "notes" in data:
        book.notes = str(data["notes"]).strip() or None

    if "status" in data:
        if data["status"] not in Book.BOOK_STATUSES:
            return jsonify({
                "error": f"Invalid status. Allowed values: {', '.join(Book.BOOK_STATUSES)}."
            }), 400
        book.status = data["status"]

    db.session.commit()

    return jsonify(book_to_dict(book)), 200


# DELETE /api/v1/books/<id>
@api_bp.route("/books/<int:book_id>", methods=["DELETE"])
@login_required
def api_book_delete_handler(book_id: int):
    book = Book.query.get_or_404(book_id)

    if book.user_id != current_user.id:
        return jsonify({
            "error": "Access forbidden."
        }), 403

    db.session.delete(book)
    db.session.commit()

    return jsonify({"message": f"Book #{book_id} has been deleted"}), 200


# GET /api/v1/stats
@api_bp.route("/stats", methods=["GET"])
@login_required
def api_stats_handler():
    books: list[Book] = Book.query.filter_by(user_id=current_user.id).all()

    # Stats
    total = len(books)
    wanted = sum(1 for b in books if b.status == "wanted")
    reading = sum(1 for b in books if b.status == "reading")
    read = sum(1 for b in books if b.status == "read")

    from_google = sum(1 for b in books if b.google_id)
    manual = total - from_google

    return jsonify({
        "total": total,
        "by_status": {
            "wanted": wanted,
            "reading": reading,
            "read": read,
        },
        "by_source": {
            "google_books": from_google,
            "manual": manual
        }
    }), 200
