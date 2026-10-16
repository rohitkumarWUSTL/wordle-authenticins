# Wordle Full Stack Assessment

## Write-up

Most of the codebase is self-explanatory. On the backend, I used a three-tier architecture pattern to separate the API definition, application logic, and data interfacing; while I leaned more on AI tools for generating the frontend, I made sure to document the file structure, conventions, and API in the frontend README - both for my own understanding and so a fresh agentic session could more easily maneuver the codebase and implement changes. However, I still wanted to include a brief writeup to talk about the dictionary:

- Figuring out a source of truth to generate answers and validate guesses against was an interesting challenge. Similar to the original Wordle game, I wanted answers to generally
be more common words, but couldn't just use the "official" list of words Wordle uses, since I need to support 6, 7, and 8 letter games. I generate the dictionary (both valid answers and valid guesses, which are two separate lists) .txt files in the generate_words.py script by pulling from TWL06.txt (official Scrabble tournament word list) to exclude proper nouns and abbreviations; I sort, filter, and (for randomly selecting answers) weight words by their frequency per the `wordfreq` library. Answers are the top 2500 words by wordfreq zipf frequency above a 3.5 floor and guesses are the top 15000 above a 2.0 floor; this allows for more common words to be selected as answers while still being permissive in what guesses are allowed.
- Sourcing from TWL06 and sorting/filtering on frequency can lead to odd edge cases - a word that is rare as a non-proper noun but common as a proper noun (e.g. "henry", which is a unit of electrical inductance but also a very common name) - can be allowed as an answer, even though it goes against the intention of my algorithm. This was a tradeoff I was willing to accept; if I absolutely needed to eliminate it, I would find a case-sensitive word frequency source of truth or, short of that, train some sort of classifier that passed an acceptable threshold. 
- I used a rough heuristic (-s, -es, -ies, -ves) to eliminate plural words, which I think is consistent enough with how official Wordle selects words as well, since irregular plural words like "geese", "cacti", and "women" appear in Wordle lists (https://gist.github.com/cfreshman/a03ef2cba789d8cf00c08f767e0fad7b).   
- I keep answers and valid guesses in two separate sections within each text file (the text files being partitioned by word length); I wanted to keep them decoupled/redundant so that a change in the answer pool wouldn't affect the guess pool and vice versa.
- The dictionary .txt files are generated through the generate_words.py script by Docker when starting up the service, and also regenerated on-demand during runtime as needed. On runtime, they are read into memory for answer generation and guess lookups. It likely would've been more performant and technically sound to seed a Redis cache, but I opted for in-memory loading for simplicity's sake, given the dictionary was small enough to do so without significant penalty.

## Background

Wordle is a simple game in which you have to guess a five-letter word. You get six guesses, learning a little more information with each guess, and eventually narrow your guesses down to find the answer.

You can play an online version of Wordle [here](https://www.nytimes.com/games/wordle/index.html).

## Rules

1. Letters that are in the answer and in the right place turn green.
2. Letters that are in the answer but in the wrong place turn yellow.
3. Letters that are not in the answer turn gray.
4. Answers are never plural.
5. Letters can appear more than once. So if your guess includes two of one letter, they may both turn yellow, both turn green, or one could be yellow and the other green.
6. Each guess must be a valid word in Wordle's dictionary. You can't guess ABCDE, for instance.
7. You do not have to include correct letters in subsequent guesses.
8. You have six guesses to solve the Wordle.

## Goal

Your goal is to design and build a full stack Wordle application with both a REST API backend and a React frontend.

In our version of Wordle, there are 2 key differences from the original:

1. **Multiple Games**: The user can create and play as many games as they want.
2. **Configurable Word Length**: The user can configure the number of letters in the target word to be anywhere between 5 to 8 letters, but they will always only have N+1 turns to guess the word. For instance, traditional Wordle involves guessing a five-letter word over six turns, but in our version, the user can pick 7 as the number of letters and get 8 turns to guess the word.

### Backend Requirements

- Build a REST API that supports:
  - Creating a new game (with configurable word length 5-8)
  - Submitting guesses and receiving feedback (green/yellow/gray for each letter)
  - Retrieving game state
  - Validating that guesses are real words
- Use appropriate data storage for game state

### Frontend Requirements

- Build a React UI that allows users to:
  - Start a new game with a selected word length (5-8 letters)
  - Enter guesses via an on-screen keyboard or physical keyboard
  - See feedback for each guess (green/yellow/gray letters)
  - View their guess history for the current game
  - See when they've won or lost

**Use of AI is allowed and encouraged for this assessment.**

---

## Getting Started

This repository includes boilerplate code to help you get started quickly.

### Project Structure

```
wordle-starter/
├── frontend/           # React application (Vite)
├── backend/            # FastAPI application
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

### Frontend

The frontend is a React application built with Vite. It is pre-configured with CORS support to communicate with the backend.

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`.

**Key files to modify:**
- `frontend/src/App.jsx` - Main application component, start building your UI here
- `frontend/src/App.css` - Application styles
- Add new components in `frontend/src/components/` as needed

### Backend

The backend is a FastAPI application with CORS already configured for the frontend. Run it using Docker Compose:

```bash
docker compose up --build
```

This will build and start the backend container with hot-reloading enabled. The API will be available at `http://localhost:8000`.

To run in detached mode (background):

```bash
docker compose up -d --build
```

To run unit tests, after running the container in detached mode:

```bash
docker compose exec backend pytest
```

To stop the container:

```bash
docker compose down
```

API documentation is automatically available at `http://localhost:8000/docs`.

### Backend Services

The backend uses one supporting service, started automatically by `docker compose up`:

- **SQLite** — file-based database, no setup required. The database file lives at `backend/data/wordle.db` (mounted into the container at `/app/data/wordle.db`). The schema is created automatically on startup from the SQLAlchemy models in `backend/app/models/`. To reset the database, delete `backend/data/wordle.db` and restart the backend.

The word list is generated at build time into `backend/app/data/words_{length}.txt` (one file per supported word length). If a file is missing at runtime, `app/dictionary.py` regenerates it on demand.

#### Environment variables

The backend reads the following environment variables (see `backend/.env.example`):

| Variable       | Default                                   | Description                   |
| -------------- | ----------------------------------------- | ----------------------------- |
| `DATABASE_URL` | `sqlite+aiosqlite:////app/data/wordle.db` | SQLAlchemy async database URL |

#### Health check

`GET /health` returns the status of the backend and its dependencies:

```json
{ "status": "healthy", "db": "ok" }
```

### Development Workflow

1. Start the backend with `docker compose up --build`
2. Start the frontend with `cd frontend && npm install && npm run dev`
3. Build your API endpoints in `backend/main.py`
4. Build your UI in the `frontend/src/` directory
5. The frontend is configured to make requests to `http://localhost:8000`
