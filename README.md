# IMDB Movie Database Project

A full-stack movie database web application built on the IMDB Top 1000 dataset, supporting browsing, searching, statistics, and AI-powered natural language queries.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vanilla HTML/CSS/JS + Tailwind CSS (CDN) |
| Backend | Flask + Flask-CORS |
| Database | SQLite |
| AI | Google Gemini API (NL2SQL) |
| SQL Validation | sqlglot |

## Main Features

- **Movie Browsing**: Paginated movie list with filtering by title, genre, director, and year
- **Movie Details**: Full movie info including cast, genres, ratings, and gross revenue
- **Actor / Director Pages**: Filmography and profile for each person
- **Statistics**: Genre distribution, top-rated movies, rating trends
- **NL2SQL Query**: Natural language queries translated to SQL via Gemini API (4 prompt strategies)

## Project Structure

```
imdb_database/
├── run.py                  # Entry point: initializes DB and starts the app
├── createTable.py          # Parses IMDB CSV and builds normalized SQLite tables
├── operate_funcs.py        # MovieDatabase class with CRUD operations
├── db2sql.py               # SQLite → MySQL migration tool
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template (Gemini API key)
├── imdb_top_1000.csv       # Source dataset
├── movies.db               # SQLite database (auto-generated)
│
├── backend/
│   ├── app.py              # Flask REST API server (port 7777)
│   └── API_DOC.md          # API endpoint documentation
│
├── frontend/
│   ├── index.html          # Home page: search, movie list, NL2SQL interface
│   ├── movie.html          # Movie detail page
│   ├── actor.html          # Actor detail page
│   ├── director.html       # Director detail page
│   ├── stats.html          # Statistics and analytics page
│   ├── css/
│   │   └── style.css       # Global styles
│   ├── js/
│   │   ├── api.js          # Unified API client (base: http://127.0.0.1:7777/api)
│   │   ├── home.js         # Home page logic: search, NL2SQL, movie list rendering
│   │   ├── movie.js        # Movie detail page logic
│   │   ├── actor.js        # Actor detail page logic
│   │   ├── director.js     # Director detail page logic
│   │   └── stats.js        # Statistics page logic
│   └── assets/             # Placeholder images
│
└── llm/
    ├── llm_service.py      # NL2SQL core: LLMQueryService with 4 prompt strategies
    ├── run_prompt_eval.py  # Evaluation framework for NL2SQL strategies
    ├── nl2sql_eval_set.json           # Standard evaluation dataset
    ├── nl2sql_eval_set_stress.json    # Stress test evaluation dataset
    └── eval_results_*.jsonl           # Per-strategy evaluation results
```

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env.example` to `.env` and fill in your Gemini API key:

```
GEMINI_API_KEY=your_api_key_here
```

### 3. Initialize the database

```bash
python createTable.py
```

### 4. Start the backend

```bash
python backend/app.py
```

The API server runs at `http://127.0.0.1:7777`.

### 5. Open the frontend

Open `frontend/index.html` directly in a browser (no build step required).

---

## NL2SQL Strategies

The LLM service (`llm/llm_service.py`) supports 4 prompt strategies for natural language to SQL translation:

| Strategy | Description |
|----------|-------------|
| `zero-shot` | Direct translation with schema context only |
| `few-shot` | Includes example query/SQL pairs |
| `constrained` | Adds explicit SQL constraints and rules |
| `hybrid` | Combines few-shot examples with constraints |

---

## API Documentation

Full API documentation: [`backend/API_DOC.md`](backend/API_DOC.md)