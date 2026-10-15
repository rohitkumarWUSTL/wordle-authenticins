# Wordle Frontend

React + Vite single-page app for the Wordle backend. Talks to the FastAPI
backend over HTTP.

## Dev commands

```bash
npm install
npm run dev      # start Vite dev server (default http://localhost:5173)
npm run build    # production build
npm run lint     # eslint
```

The backend is expected to be running at `http://localhost:8000` (see
`src/api/client.js` → `API_URL`). CORS is handled on the backend side.

## Running in GitHub Codespaces

Codespaces forwards each port to its own HTTPS URL, so `localhost:8000` in
the browser does not reach the backend. `src/api/client.js` detects the
`.app.github.dev` hostname and rewrites the port from `5173` (frontend) to
`8000` (backend) automatically — no configuration needed.

The backend's CORS config in `backend/main.py` allows both
`http://localhost:5173` and any `https://<codespace>-5173.app.github.dev`
origin (via `allow_origin_regex`).

If you change the frontend or backend port, update the rewrite in
`client.js` and the regex in `main.py` accordingly.

## File structure

```
src/
  main.jsx                    # entry point; wraps <App/> in <BrowserRouter>
  App.jsx                     # route table only
  constants.js                # MIN/MAX_WORD_LENGTH, WORD_LENGTHS, PAGE_SIZE, status values
  api/
    client.js                 # API_URL + fetch wrapper (throws on non-2xx)
    games.js                  # listGames, createGame, getGame
  pages/
    GamesPage.jsx             # /games — list, filter, pagination, new-game modal
    GameDetailPage.jsx        # /games/:id — placeholder for now
  components/
    GameList.jsx              # renders a list of GameListItem
    GameListItem.jsx          # one row: name, status, guesses, last guess; links to detail
    NewGameButton.jsx         # "Start new game" (full) or "+" (compact) variants
    NewGameModal.jsx          # <dialog>-based modal with word-length radios
    Pagination.jsx            # prev/next + "Page X of Y"
    StatusFilter.jsx          # <select> for All / Active games
  App.css                     # component styles
  index.css                   # global styles
```

## Routing

| Path          | Component         | Notes                                    |
| ------------- | ----------------- | ---------------------------------------- |
| `/`           | redirect          | → `/games`                               |
| `/games`      | `GamesPage`       | list + filter + pagination               |
| `/games/:id`  | `GameDetailPage`  | placeholder; will become the play view   |

## API contract

Base URL: `http://localhost:8000` locally, or the Codespaces-forwarded
`https://<codespace>-8000.app.github.dev` (resolved automatically).

### `GET /games`

Query params:

- `status` (optional) — one of `IN_PROGRESS`, `WON`, `LOST`. Omit for all.
- `limit` (default 20, 1–100)
- `offset` (default 0)

Response:

```json
{
  "items": [
    {
      "id": 1,
      "word_length": 5,
      "status": "IN_PROGRESS",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "guesses": [
        { "word": "apple", "guess_number": 1, "feedback": [ ... ] }
      ]
    }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

### `POST /games`

Body: `{ "word_length": 5 }` (5–8). Returns a single game object (same shape
as an item above).

### `GET /games/:id`

Returns a single game object. 404 if not found.

## Conventions

- **Filter values**: frontend state uses `'ALL'` or `'IN_PROGRESS'`. `'ALL'`
  is mapped to *omitting* the `status` query param in `api/games.js`.
- **Page size**: `PAGE_SIZE = 20` (matches backend default).
- **Filter change resets pagination**: changing the status filter sets
  `offset` back to `0` (see `GamesPage.handleStatusChange`).
- **Word length constants**: `MIN_WORD_LENGTH = 5`, `MAX_WORD_LENGTH = 8`,
  hardcoded in `src/constants.js` to mirror `backend/app/constants.py`.
- **Total allowed guesses**: `word_length + 1` (mirrors the backend's
  `_resolve_status` rule in `game_service.py`).
- **Game list row** shows: `Game {id}`, status label, `{guesses.length} /
  {word_length + 1}`, and the last guess word (or `—` if none).
- **New game flow**: modal → `POST /games` → navigate to `/games/:id`.
- **Status labels**: `IN_PROGRESS` → "In progress", `WON` → "Won",
  `LOST` → "Lost" (see `GameListItem.jsx`).

## Notes for future work

- `GameDetailPage` is a placeholder; the play view (guess input, feedback
  grid) is not implemented yet.
- No global state library; each page fetches what it needs.
- No tests yet on the frontend.
- `react-router-dom` v7 is used; routes are declared in `App.jsx`.
