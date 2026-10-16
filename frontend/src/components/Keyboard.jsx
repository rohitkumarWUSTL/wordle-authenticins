import { KEYBOARD_ROWS } from '../constants.js'

const COLOR_CLASS = {
  GREEN: 'keyboard-key-green',
  YELLOW: 'keyboard-key-yellow',
  GRAY: 'keyboard-key-gray',
}

function Keyboard({ onKey, onEnter, onBackspace, letterStates, disabled }) {
  const handleClick = (key) => {
    if (disabled) return
    if (key === 'ENTER') {
      onEnter()
    } else if (key === 'BACKSPACE') {
      onBackspace()
    } else {
      onKey(key)
    }
  }

  return (
    <div className="keyboard">
      {KEYBOARD_ROWS.map((row, rowIndex) => (
        <div key={rowIndex} className="keyboard-row">
          {row.map((key) => {
            const isWide = key === 'ENTER' || key === 'BACKSPACE'
            const state = letterStates[key]
            const colorClass = state ? COLOR_CLASS[state] || '' : ''
            return (
              <button
                key={key}
                type="button"
                className={`keyboard-key ${isWide ? 'keyboard-key-wide' : ''} ${colorClass}`.trim()}
                onClick={() => handleClick(key)}
                disabled={disabled}
              >
                {key === 'BACKSPACE' ? '⌫' : key}
              </button>
            )
          })}
        </div>
      ))}
    </div>
  )
}

export default Keyboard
