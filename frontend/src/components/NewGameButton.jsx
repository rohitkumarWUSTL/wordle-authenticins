import { WORD_LENGTHS } from '../constants.js'

function NewGameButton({ variant, onCreate, disabled = false }) {
  const handleChange = (event) => {
    const wordLength = Number(event.target.value)
    if (!wordLength) return
    onCreate(wordLength)
    // Reset so the same option can be chosen again later.
    event.target.value = ''
  }

  const isCompact = variant === 'compact'

  return (
    <span className="new-game-button-wrapper">
      <span
        className={`new-game-button ${
          isCompact ? 'new-game-button-compact' : 'new-game-button-full'
        }`}
        aria-hidden="true"
      >
        {isCompact ? '+' : 'Start new game'}
      </span>
      <select
        className="new-game-button-select"
        onChange={handleChange}
        disabled={disabled}
        defaultValue=""
        aria-label="Start new game"
        title="Start new game"
      >
        <option value="" disabled hidden />
        {WORD_LENGTHS.map((length) => (
          <option key={length} value={length}>
            Word length: {length} letters
          </option>
        ))}
      </select>
    </span>
  )
}

export default NewGameButton
