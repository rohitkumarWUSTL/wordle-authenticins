import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createGame, listGames } from '../api/games.js'
import { PAGE_SIZE, STATUS_ALL } from '../constants.js'
import GameList from '../components/GameList.jsx'
import NewGameButton from '../components/NewGameButton.jsx'
import Pagination from '../components/Pagination.jsx'
import StatusFilter from '../components/StatusFilter.jsx'

function GamesPage() {
  const navigate = useNavigate()
  const [games, setGames] = useState([])
  const [total, setTotal] = useState(0)
  const [status, setStatus] = useState(STATUS_ALL)
  const [offset, setOffset] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [creating, setCreating] = useState(false)

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

  const handleStatusChange = useCallback((next) => {
    // Reset the data and flip into the loading state in the same render as
    // the status change, so we never paint a frame with the new filter and
    // the old (stale) total. Without this, switching to an empty filter can
    // briefly flash the full-width empty state.
    setStatus(next)
    setOffset(0)
    setGames([])
    setTotal(0)
    setLoading(true)
  }, [])

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
            onChange={setOffset}
          />
        </>
      )}
    </div>
  )
}

export default GamesPage
