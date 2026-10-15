import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createGame, listGames } from '../api/games.js'
import { PAGE_SIZE, STATUS_ALL } from '../constants.js'
import GameList from '../components/GameList.jsx'
import NewGameButton from '../components/NewGameButton.jsx'
import NewGameModal from '../components/NewGameModal.jsx'
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
  const [showNewGame, setShowNewGame] = useState(false)

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
    setStatus(next)
    setOffset(0)
  }, [])

  const handleCreate = useCallback(
    async (wordLength) => {
      const game = await createGame({ wordLength })
      setShowNewGame(false)
      navigate(`/games/${game.id}`)
    },
    [navigate],
  )

  const isEmpty = !loading && !error && total === 0

  return (
    <div className="games-page">
      <header className="games-header">
        <h1>Wordle</h1>
        {!isEmpty && (
          <div className="games-header-actions">
            <StatusFilter value={status} onChange={handleStatusChange} />
            <NewGameButton variant="compact" onClick={() => setShowNewGame(true)} />
          </div>
        )}
      </header>

      {loading && <p className="games-status">Loading…</p>}
      {error && <p className="games-status games-error">Error: {error}</p>}

      {isEmpty && (
        <div className="games-empty">
          <NewGameButton
            variant="full"
            onClick={() => setShowNewGame(true)}
          />
        </div>
      )}

      {!loading && !error && !isEmpty && (
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

      <NewGameModal
        open={showNewGame}
        onClose={() => setShowNewGame(false)}
        onCreate={handleCreate}
      />
    </div>
  )
}

export default GamesPage
