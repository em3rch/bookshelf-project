# Final project for *Programowanie komputerów" university subject by Artem Yevtushenko

# Setup Instructions

## Prerequisites

- A Google Books API key ([get one here](https://console.cloud.google.com))

---

## 1. Clone the Repository

```bash
git clone <your-repository-url>
cd bookshelf-project
```

---

## 2. Create a Virtual Environment

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Copy the example file:

**macOS / Linux:**
```bash
cp .env.example .env
```

**Windows (Command Prompt):**
```cmd
copy .env.example .env
```

Then open `.env` in any text editor and fill in your values:

```env
SECRET_KEY=your-random-secret-key-here
DATABASE_URL=sqlite:///bookshelf.db
GOOGLE_BOOKS_API_KEY=your-google-books-api-key-here
```

**`SECRET_KEY`** — any long random string. You can generate one by running:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**`GOOGLE_BOOKS_API_KEY`** — the key you obtained from Google Cloud Console.

---

## 5. Initialize the Database

```bash
flask init-db
```

This creates the `app/instance/bookshelf.db` file with all required tables.

---

## 6. Create the Uploads Folder

The app stores user-uploaded book covers here. Create the folder manually if it doesn't exist:

**macOS / Linux:**
```bash
mkdir -p app/static/uploads/covers
```

**Windows (Command Prompt):**
```cmd
mkdir app\static\uploads\covers
```

---

## 7. Run the Application

```bash
flask run
```

Open your browser and go to: [http://localhost:5000](http://localhost:5000)

---

## 8. Testing the API with Postman

The app exposes a REST API at `/api/v1/`. To test it:

1. Open Postman and make sure **"Automatically follow redirects"** is enabled.
2. Make sure **cookies are enabled** in Postman — the API uses session-based authentication.

**Register:**
```
POST http://localhost:5000/api/v1/auth/register
Content-Type: application/json

{
  "username": "john",
  "email": "john@example.com",
  "password": "secret123"
}
```

**Login:**
```
POST http://localhost:5000/api/v1/auth/login
Content-Type: application/json

{
  "username_or_email": "john",
  "password": "secret123"
}
```
