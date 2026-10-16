import { Link } from 'react-router-dom'

const STATUS_LABELS = {
  IN_PROGRESS: 'In progress',
  WON: 'Won',
  LOST: 'Lost',
}

const COLOR_CLASS = {
  GREEN: 'guess-cell-green',
  YELLOW: 'guess-cell-yellow',
  GRAY: 'guess-cell-gray',
}

function GameListItem({ game }) {
  const guesses = game.guesses || []
  const totalAllowed = game.word_length + 1
  const lastGuess = guesses.length > 0 ? guesses[guesses.length - 1] : null

  return (
    <li className="game-list-item">
      <Link to={`/games/${game.id}`} className="game-list-item-link">
        <span className="game-list-item-name">Game {game.id}</span>
        <span className={`game-list-item-status status-${game.status.toLowerCase()}`}>
          {STATUS_LABELS[game.status] || game.status}
        </span>
        <span className="game-list-item-guesses">
          {guesses.length} / {totalAllowed}
        </span>
        <span className="game-list-item-last-guess">
          {lastGuess ? (
            lastGuess.feedback.map((item) => (
              <span
                key={item.index}
                className={`guess-cell guess-cell-small ${COLOR_CLASS[item.color] || ''}`.trim()}
              >
                {item.letter}
              </span>
            ))
          ) : (
            <span className="game-list-item-empty">—</span>
          )}
        </span>
      </Link>
    </li>
  )
}

export default GameListItem
