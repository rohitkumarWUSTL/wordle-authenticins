import GameListItem from './GameListItem.jsx'

function GameList({ games }) {
  return (
    <ul className="game-list">
      {games.map((game) => (
        <GameListItem key={game.id} game={game} />
      ))}
    </ul>
  )
}

export default GameList
