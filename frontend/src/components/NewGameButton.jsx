import { MIN_WORD_LENGTH, WORD_LENGTHS } from '../constants.js'

function NewGameButton({ variant, onCreate, disabled = false }) {
  const handleChange = (event) => {
    const wordLength = Number(event.target.value)
    if (!wordLength) return
    onCreate(wordLength)
    // Reset so the same option can be chosen again later.
    event.target.value = ''
  }

  if (variant === 'compact') {
    return (
      <select
        className="new-game-button new-game-button-compact"
        onChange={handleChange}
        disabled={disabled}
        defaultValue=""
        aria-label="Start new game"
        title="Start new game"
      >
        <option value="" disabled hidden>
          +
        </option>
        {WORD_LENGTHS.map((length) => (
          <option key={length} value={length}>
            Word length: {length} letters
          </option>
        ))}
      </select>
    )
  }

  return (
    <select
      className="new-game-button new-game-button-full"
      onChange={handleChange}
      disabled={disabled}
      defaultValue=""
      aria-label="Start new game"
    >
      <option value="" disabled hidden>
        Start new game
      </option>
      {WORD_LENGTHS.map((length) => (
        <option key={length} value={length}>
          Word length: {length} letters
        </option>
      ))}
    </select>
  )
}

export default NewGameButton
