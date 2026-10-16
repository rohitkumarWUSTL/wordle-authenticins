import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { createGame, listGames } from '../api/games.js'
import { PAGE_SIZE, STATUS_ALL } from '../constants.js'
import GameList from '../components/GameList.jsx'
import NewGameButton from '../components/NewGameButton.jsx'
import Pagination from '../components/Pagination.jsx'
import StatusFilter from '../components/StatusFilter.jsx'

function GamesPage() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const [games, setGames] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [creating, setCreating] = useState(false)

  // The list state lives in the URL so that navigating to a game and back
  // (via the "Back to games" link) restores the same filter and page, and
  // so the state survives a refresh.
  const status = searchParams.get('status') || STATUS_ALL
  const offset = Number(searchParams.get('offset')) || 0

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    listGames({ status, limit: PAGE_SIZE, offset })
      .then((data) => {
        if (cancelled) return
        setGames(data.items)
        setTotal(data.total)
      })
      .catch((err) => {
        if (cancelled) return
        setError(err.message)
      })
      .finally(() => {
        if (cancelled) return
        setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [status, offset])

  const handleStatusChange = useCallback(
    (next) => {
      // Reset the data and flip into the loading state in the same render as
      // the status change, so we never paint a frame with the new filter and
      // the old (stale) total. Without this, switching to an empty filter can
      // briefly flash the full-width empty state.
      setGames([])
      setTotal(0)
      setLoading(true)
      const params = new URLSearchParams()
      if (next && next !== STATUS_ALL) {
        params.set('status', next)
      }
      setSearchParams(params)
    },
    [setSearchParams],
  )

  const handleOffsetChange = useCallback(
    (next) => {
      const params = new URLSearchParams(searchParams)
      if (next > 0) {
        params.set('offset', String(next))
      } else {
        params.delete('offset')
      }
      setSearchParams(params)
    },
    [searchParams, setSearchParams],
  )

  const handleCreate = useCallback(
    async (wordLength) => {
      setCreating(true)
      try {
        const game = await createGame({ wordLength })
        navigate(`/games/${game.id}`)
      } catch (err) {
        setError(err.message)
        setCreating(false)
      }
    },
    [navigate],
  )

  const hasFilter = status !== STATUS_ALL
  const isEmpty = !loading && !error && total === 0 && !hasFilter
  const isFilteredEmpty = !loading && !error && total === 0 && hasFilter

  return (
    <div className="games-page">
      {!isEmpty && (
        <header className="games-header">
          <h1>Wordle</h1>
          <div className="games-header-actions">
            <StatusFilter value={status} onChange={handleStatusChange} />
            <NewGameButton
              variant="compact"
              onCreate={handleCreate}
              disabled={creating}
            />
          </div>
        </header>
      )}

      {loading && <p className="games-status">Loading…</p>}
      {error && <p className="games-status games-error">Error: {error}</p>}

      {isEmpty && (
        <div className="games-empty">
          <NewGameButton
            variant="full"
            onCreate={handleCreate}
            disabled={creating}
          />
        </div>
      )}

      {isFilteredEmpty && (
        <p className="games-status">No games match this filter.</p>
      )}

      {!loading && !error && !isEmpty && !isFilteredEmpty && (
        <>
          <GameList games={games} />
          <Pagination
            total={total}
            limit={PAGE_SIZE}
            offset={offset}
            onChange={handleOffsetChange}
          />
        </>
      )}
    </div>
  )
}

export default GamesPage
