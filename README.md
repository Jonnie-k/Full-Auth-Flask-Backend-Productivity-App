# Notes App — Full Auth Flask Backend

A secure RESTful Flask API for a personal notes productivity app. Users can register, log in, and manage their own private notes with full CRUD operations and pagination. Authentication is handled via JWT (JSON Web Tokens).

---

## Features

- JWT-based authentication (signup, login, logout, /me)
- User-owned notes with full CRUD
- Pagination on the notes index route
- Protected routes — users can only access their own data
- Password hashing with Flask-Bcrypt
- Input validation with Marshmallow
- Database seeding with Faker

---

## Installation

**Prerequisites:** Python 3.8+, Pipenv

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd "Full Auth Flask Backend- Productivity App"

# 2. Install dependencies
pipenv install

# 3. Activate the virtual environment
pipenv shell

# 4. Set up environment variables
cp .env.example .env
# Edit .env and set a strong JWT_SECRET_KEY for production

# 5. Initialize and migrate the database
flask db init
flask db migrate -m "initial migration"
flask db upgrade

# 6. Seed the database
python seed.py

---

## Running the App

flask run

The API will be available at `http://127.0.0.1:5000`.

---

## Running Tests

pytest

---

## API Endpoints

### Auth

| Method | Endpoint       | Auth Required | Description                        |
|--------|----------------|---------------|------------------------------------|
| POST   | /auth/signup   | No            | Register a new user                |
| POST   | /auth/login    | No            | Log in and receive a JWT token     |
| DELETE | /auth/logout   | Yes           | Revoke the current JWT token       |
| GET    | /auth/me       | Yes           | Get the currently logged-in user   |

### Notes

All notes endpoints require the `Authorization: Bearer <token>` header.

| Method | Endpoint           | Description                          |
|--------|--------------------|--------------------------------------|
| GET    | /notes             | Get all notes (paginated)            |
| GET    | /notes/:id         | Get a single note                    |
| POST   | /notes             | Create a new note                    |
| PATCH  | /notes/:id         | Update a note (partial update)       |
| DELETE | /notes/:id         | Delete a note                        |

## Test Credentials (after seeding)

username: testuser
password: password123

### Author
John King'oo