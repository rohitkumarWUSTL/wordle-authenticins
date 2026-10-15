import { Link, useParams } from 'react-router-dom'

function GameDetailPage() {
  const { id } = useParams()

  return (
    <div className="game-detail-page">
      <p>
        <Link to="/games">← Back to games</Link>
      </p>
      <h1>Game {id}</h1>
      <p className="game-detail-placeholder">
        Game detail view coming soon.
      </p>
    </div>
  )
}

export default GameDetailPage
