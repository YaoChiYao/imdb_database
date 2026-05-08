# IMDB Movie Database Project

A full-stack movie database web application that supports browsing, searching, user ratings and favorites, and AI-powered Q&A functionality.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + Vite + React Router |
| Backend | Flask + Flask-CORS |
| Database | MySQL |
| AI | Anthropic Claude API |

## Main Features

- **Movie Browsing**: Paginated movie list with filtering by title, genre, and year, plus search functionality  
- **Movie Details**: View detailed information, user reviews, and ratings  
- **User System**: Register, login (JWT authentication), and profile page  
- **Favorites and Ratings**: Logged-in users can favorite movies, submit ratings, and leave reviews  
- **AI Q&A**: Integrated Claude API for natural language queries about movies  

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```
---

## Environment Configuration

In backend/config.py, set the following:

```python
DB_HOST = "localhost"
DB_USER = "your_db_user"
DB_PASSWORD = "your_db_password"
DB_NAME = "imdb_database"
JWT_SECRET = "your_jwt_secret"
CLAUDE_API_KEY = "your_anthropic_api_key"
```

---

## API Documentation

Full API documentation is available at ./backend/API_DOC.md