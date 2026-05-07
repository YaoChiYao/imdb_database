# IMDB Movie Database — API Documentation

**Backend**: Flask + SQLite (`movies.db`)
**Base URL**: `http://127.0.0.1:7777`

---

## Getting Started

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# fill GEMINI_API_KEY in .env
python app.py
```

The server runs at `http://127.0.0.1:7777` with debug mode enabled.

Notes:
- Recommended LLM provider: `LLM_PROVIDER=gemini` + `GEMINI_API_KEY`.
- Default model can be set via `LLM_MODEL=gemini-3-flash-preview` (or `GEMINI_MODEL`).
- API retry backoff can be enabled via `LLM_MAX_RETRIES` and `LLM_RETRY_BASE_SEC` to handle transient timeouts.
- Installing `sqlglot` is recommended to enable the local AST safety gateway for stricter dangerous SQL filtering.

---

## Endpoints

### 0. Natural Language to SQL Query (LLM)

| Field    | Value             |
|----------|-------------------|
| Method   | `POST`            |
| Endpoint | `/api/query/nl`   |

**Request Body**

```json
{
    "query": "show top 5 sci-fi movies after 2010",
    "strategy": "hybrid"
}
```

- `query`: Natural language question (required)
- `strategy`: Prompt strategy (optional). One of `zero-shot` / `few-shot` / `constrained` / `hybrid`. Defaults to `hybrid` (recommended).

**Success Response**

```json
{
    "generated_sql": "SELECT ... LIMIT 50",
    "latency_ms": 132,
    "query": "show top 5 sci-fi movies after 2010",
    "result_count": 5,
    "react_rounds": 0,
    "react_trace": [],
    "results": [
        {
            "movie_id": 130,
            "title": "Inception",
            "imdb_rating": 8.8,
            "year": 2010
        }
    ],
    "strategy": "hybrid"
}
```

**Reliability Mechanisms**

- Local AST safety gateway (requires `sqlglot`):
    - Only allows `SELECT` / `WITH ... SELECT`
    - Blocks destructive statements: `DROP/DELETE/TRUNCATE/UPDATE/INSERT/ALTER/CREATE`
    - Whitelist-only table access
    - Automatically appends `LIMIT` for non-aggregate list queries
- ReAct correction loop:
    - If SQL parsing or execution fails, the error is fed back to the model for SQL rewrite
    - `react_trace` records each failed SQL attempt and its error

**Error Response**

```json
{
    "error": "Only SELECT (or WITH...SELECT) queries are allowed.",
    "query": "drop table Movie",
    "result_count": 0,
    "results": [],
    "strategy": "hybrid"
}
```

---

### 0.1 Natural Language Recommendation Query (LLM)

| Field    | Value                  |
|----------|------------------------|
| Method   | `POST`                 |
| Endpoint | `/api/recommend/nl`    |

**Request Body**

```json
{
    "query": "recommend emotional drama movies",
    "strategy": "hybrid"
}
```

Response structure is identical to `/api/query/nl`. The main difference is that the prompt is tuned toward recommendation ranking.

---

### 1. Get Movie Details

| Field    | Value                  |
|----------|------------------------|
| Method   | `GET`                  |
| Endpoint | `/api/movies/<id>`     |

**Path Parameters**

| Parameter | Type | Description          |
|-----------|------|----------------------|
| `id`      | int  | The movie's `movie_id` |

Returns full details for a movie, including director name, actor list, and genre list.

**Request Example**

```
GET http://127.0.0.1:7777/api/movies/1
```

**Response Example**

```json
{
    "certificate": "A",
    "director_id": 1,
    "director_name": "Frank Darabont",
    "gross": 28341469.0,
    "imdb_rating": 9.3,
    "meta_score": 80.0,
    "movie_id": 1,
    "overview": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
    "poster_link": "https://m.media-amazon.com/images/...",
    "runtime": 142,
    "title": "The Shawshank Redemption",
    "votes": 2343110,
    "year": 1994,
    "actors": [
        { "actor_id": 1, "actor_name": "Tim Robbins" },
        { "actor_id": 2, "actor_name": "Morgan Freeman" }
    ],
    "genres": [
        { "genre_id": 1, "genre": "Drama" }
    ]
}
```

**Error Response (Movie Not Found)**

```json
{ "error": "Movie ID 999 not found" }
```

HTTP Status: `404`

---

### 2. Filter Movies by Genre

| Field    | Value                           |
|----------|---------------------------------|
| Method   | `GET`                           |
| Endpoint | `/api/movies/genre/<genre>`     |

**Path Parameters**

| Parameter | Type   | Description                        |
|-----------|--------|------------------------------------|
| `genre`   | string | Genre name, e.g. `Drama`, `Action` |

Returns all movies in the specified genre, including director name, sorted by `imdb_rating` descending.

**Request Examples**

```
GET http://127.0.0.1:7777/api/movies/genre/Drama
GET http://127.0.0.1:7777/api/movies/genre/Action
```

**Response Example**

```json
[
    {
        "certificate": "A",
        "director_name": "Frank Darabont",
        "gross": 28341469.0,
        "imdb_rating": 9.3,
        "movie_id": 1,
        "overview": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
        "poster_link": "https://m.media-amazon.com/images/...",
        "runtime": 142,
        "title": "The Shawshank Redemption",
        "votes": 2343110,
        "year": 1994
    }
]
```

**Error Response (Genre Not Found)**

```json
{ "error": "Genre \"Thriller\" not found" }
```

HTTP Status: `404`

---

### 3. List Movies

| Field    | Value          |
|----------|----------------|
| Method   | `GET`          |
| Endpoint | `/api/movies`  |

**Query Parameters**

| Parameter | Type | Default | Description        |
|-----------|------|---------|--------------------|
| `limit`   | int  | 10      | Number of results  |
| `offset`  | int  | 0       | Pagination offset  |

**Request Examples**

```
GET http://127.0.0.1:7777/api/movies
GET http://127.0.0.1:7777/api/movies?limit=5&offset=0
```

**Response Example**

```json
[
    {
        "certificate": "A",
        "director_name": "Frank Darabont",
        "gross": 28341469.0,
        "imdb_rating": 9.3,
        "meta_score": 80.0,
        "movie_id": 1,
        "overview": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
        "poster_link": "https://m.media-amazon.com/images/M/MV5BMDFkYTc0MGEtZmNhMC00ZDIzLWFmNTEtODM1ZmRlYWMwMWFmXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_UX67_CR0,0,67,98_AL_.jpg",
        "runtime": 142,
        "title": "The Shawshank Redemption",
        "votes": 2343110,
        "year": 1994
    }
]
```

---

### 4. Get All Movies by Director

| Field    | Value                          |
|----------|--------------------------------|
| Method   | `GET`                          |
| Endpoint | `/api/movies/director/<id>`    |

**Path Parameters**

| Parameter | Type | Description              |
|-----------|------|--------------------------|
| `id`      | int  | The director's `director_id` |

**Request Example**

```
GET http://127.0.0.1:7777/api/movies/director/1
```

**Response Example**

```json
{
    "director": {
        "director_id": 1,
        "director_name": "Frank Darabont"
    },
    "movies": [
        {
            "certificate": "A",
            "gross": 28341469.0,
            "imdb_rating": 9.3,
            "meta_score": 80.0,
            "movie_id": 1,
            "overview": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
            "poster_link": "https://m.media-amazon.com/images/M/MV5BMDFkYTc0MGEtZmNhMC00ZDIzLWFmNTEtODM1ZmRlYWMwMWFmXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_UX67_CR0,0,67,98_AL_.jpg",
            "runtime": 142,
            "title": "The Shawshank Redemption",
            "votes": 2343110,
            "year": 1994
        },
        {
            "certificate": "A",
            "gross": 136801374.0,
            "imdb_rating": 8.6,
            "meta_score": 61.0,
            "movie_id": 26,
            "overview": "The lives of guards on Death Row are affected by one of their charges: a black man accused of child murder and rape, yet who has a mysterious gift.",
            "poster_link": "https://m.media-amazon.com/images/M/MV5BMTUxMzQyNjA5MF5BMl5BanBnXkFtZTYwOTU2NTY3._V1_UX67_CR0,0,67,98_AL_.jpg",
            "runtime": 189,
            "title": "The Green Mile",
            "votes": 1147794,
            "year": 1999
        }
    ],
    "total": 2
}
```

**Error Response (Director Not Found)**

```json
{ "error": "Director ID 999 not found" }
```

HTTP Status: `404`

---

### 5. Genre Movie Count Statistics

| Field    | Value               |
|----------|---------------------|
| Method   | `GET`               |
| Endpoint | `/api/stats/genres` |

No parameters. Genres are stored in a separate table (`Genre` + `Movie_Genre`) and counted via JOIN — no string splitting required.

**Request Example**

```
GET http://127.0.0.1:7777/api/stats/genres
```

**Response Example**

```json
[
    {
        "avg_rating": 7.96,
        "genre": "Drama",
        "genre_id": 1,
        "movie_count": 722
    },
    {
        "avg_rating": 7.9,
        "genre": "Comedy",
        "genre_id": 11,
        "movie_count": 233
    }
]
```

Results sorted by `movie_count` descending.

---

### 6. Top N Highest-Rated Movies

| Field    | Value              |
|----------|--------------------|
| Method   | `GET`              |
| Endpoint | `/api/movies/top`  |

**Query Parameters**

| Parameter | Type | Default | Description               |
|-----------|------|---------|---------------------------|
| `top_n`   | int  | 10      | Number of results (1–100) |

Ties in rating are broken by `votes` descending.

**Request Examples**

```
GET http://127.0.0.1:7777/api/movies/top
GET http://127.0.0.1:7777/api/movies/top?top_n=5
```

**Response Example**

```json
[
    {
        "certificate": "A",
        "director_name": "Frank Darabont",
        "gross": 28341469.0,
        "imdb_rating": 9.3,
        "movie_id": 1,
        "overview": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
        "poster_link": "https://m.media-amazon.com/images/M/MV5BMDFkYTc0MGEtZmNhMC00ZDIzLWFmNTEtODM1ZmRlYWMwMWFmXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_UX67_CR0,0,67,98_AL_.jpg",
        "runtime": 142,
        "title": "The Shawshank Redemption",
        "votes": 2343110,
        "year": 1994
    }
]
```

**Error Response**

```json
{ "error": "top_n must be between 1 and 100" }
```

HTTP Status: `400`

---

### 7. Average Rating by Genre

| Field    | Value                       |
|----------|-----------------------------|
| Method   | `GET`                       |
| Endpoint | `/api/stats/genres/rating`  |

No parameters. Joins `Genre`, `Movie_Genre`, and `Movie` to compute the average `imdb_rating` and total movie count per genre, sorted by average rating descending.

**Request Example**

```
GET http://127.0.0.1:7777/api/stats/genres/rating
```

**Response Example**

```json
[
    {
        "avg_rating": 8.01,
        "genre": "War",
        "genre_id": 15,
        "movie_count": 51
    },
    {
        "avg_rating": 8.0,
        "genre": "Western",
        "genre_id": 9,
        "movie_count": 20
    }
]
```

Results sorted by `avg_rating` descending.

---

### 8. Get Movies by Actor ID

| Field    | Value                           |
|----------|---------------------------------|
| Method   | `GET`                           |
| Endpoint | `/api/stats/actors/<actor_id>`  |

**Path Parameters**

| Parameter  | Type | Description           |
|------------|------|-----------------------|
| `actor_id` | int  | The actor's `actor_id` |

Returns the actor's basic info, total movie count, average rating, and full filmography (with director names), sorted by `imdb_rating` descending.

**Request Example**

```
GET http://127.0.0.1:7777/api/stats/actors/12
```

**Response Example**

```json
{
    "actor": {
        "actor_id": 12,
        "actor_name": "Clint Eastwood"
    },
    "avg_rating": 7.96,
    "movie_count": 12,
    "movies": [
        {
            "certificate": "A",
            "director_name": "Sergio Leone",
            "gross": 6100000.0,
            "imdb_rating": 8.8,
            "movie_id": 13,
            "overview": "A bounty hunting scam joins two men in an uneasy alliance against a third in a race to find a fortune in gold buried in a remote cemetery.",
            "poster_link": "https://m.media-amazon.com/images/M/MV5BOTQ5NDI3MTI4MF5BMl5BanBnXkFtZTgwNDQ4ODE5MDE@._V1_UX67_CR0,0,67,98_AL_.jpg",
            "runtime": 161,
            "title": "Il buono, il brutto, il cattivo",
            "votes": 688390,
            "year": 1966
        },
        {
            "certificate": "U",
            "director_name": "Sergio Leone",
            "gross": 15000000.0,
            "imdb_rating": 8.3,
            "movie_id": 116,
            "overview": "Two bounty hunters with the same intentions team up to track down a Western outlaw.",
            "poster_link": "https://m.media-amazon.com/images/M/MV5BNWM1NmYyM2ItMTFhNy00NDU0LThlYWUtYjQyYTJmOTY0ZmM0XkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_UX67_CR0,0,67,98_AL_.jpg",
            "runtime": 132,
            "title": "Per qualche dollaro in più",
            "votes": 232772,
            "year": 1965
        }
  ]
}
```

**Error Response (Actor Not Found)**

```json
{ "error": "Actor ID 999 not found" }
```

HTTP Status: `404`

---

## Error Format

All errors follow this structure:

```json
{ "error": "Error description" }
```

| Status Code | Meaning                                              |
|-------------|------------------------------------------------------|
| 400         | Bad request parameters (e.g. non-integer `limit`)   |
| 404         | Resource not found (e.g. director ID does not exist) |