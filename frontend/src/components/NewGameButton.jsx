function NewGameButton({ variant, onClick }) {
  if (variant === 'compact') {
    return (
      <button
        type="button"
        className="new-game-button new-game-button-compact"
        onClick={onClick}
        aria-label="Start new game"
        title="Start new game"
      >
        +
      </button>
    )
  }

  return (
    <button
      type="button"
      className="new-game-button new-game-button-full"
      onClick={onClick}
    >
      Start new game
    </button>
  )
}

export default NewGameButton
