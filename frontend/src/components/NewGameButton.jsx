import { useRef } from 'react'
import { WORD_LENGTHS } from '../constants.js'

function NewGameButton({ variant, onCreate, disabled = false }) {
  const selectRef = useRef(null)

  const handleChange = (event) => {
    const wordLength = Number(event.target.value)
    if (!wordLength) return
    onCreate(wordLength)
    // Reset so the same option can be chosen again later.
    event.target.value = ''
  }

  const openPicker = () => {
    const select = selectRef.current
    if (!select) return
    if (typeof select.showPicker === 'function') {
      try {
        select.showPicker()
        return
      } catch {
        // Fall through to click() if showPicker throws (e.g. not user-initiated).
      }
    }
    select.click()
  }

  const isCompact = variant === 'compact'

  return (
    <span className="new-game-button-wrapper">
      <button
        type="button"
        className={`new-game-button ${
          isCompact ? 'new-game-button-compact' : 'new-game-button-full'
        }`}
        onClick={openPicker}
        disabled={disabled}
        aria-label="Start new game"
        title="Start new game"
      >
        {isCompact ? '+' : 'Start new game'}
      </button>
      <select
        ref={selectRef}
        className="new-game-button-select"
        onChange={handleChange}
        disabled={disabled}
        defaultValue=""
        tabIndex={-1}
        aria-hidden="true"
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
