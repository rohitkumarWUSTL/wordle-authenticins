import { GUESS_CELL_COLOR_CLASS } from '../constants.js'

const COLOR_HEX = {
  GREEN: '#6ca965',
  YELLOW: '#c8b653',
  GRAY: '#787c7f',
}

function GuessGrid({
  guesses,
  wordLength,
  maxGuesses,
  currentGuess,
  animatingRow = -1,
  shake = false,
}) {
  const rows = []

  for (let rowIndex = 0; rowIndex < maxGuesses; rowIndex += 1) {
    const guess = guesses[rowIndex]
    const isActiveRow = !guess && rowIndex === guesses.length
    const isAnimating = rowIndex === animatingRow
    const rowClasses = ['guess-row']
    if (shake && isActiveRow) rowClasses.push('guess-row-shake')

    const cells = []

    for (let colIndex = 0; colIndex < wordLength; colIndex += 1) {
      let letter = ''
      let colorClass = ''
      let cellColor = null

      if (guess) {
        const item = guess.feedback[colIndex]
        letter = item ? item.letter : ''
        // While the flip animation is running, the color comes from the
        // animation's --cell-color variable, not the class. Applying the
        // class too would show the final color during the animation delay.
        if (!isAnimating) {
          colorClass = item ? GUESS_CELL_COLOR_CLASS[item.color] || '' : ''
        }
        cellColor = item ? COLOR_HEX[item.color] || null : null
      } else if (isActiveRow) {
        letter = currentGuess[colIndex] || ''
        colorClass = letter ? 'guess-cell-active' : ''
      }

      const cellClasses = ['guess-cell']
      if (colorClass) cellClasses.push(colorClass)
      if (isAnimating) cellClasses.push('guess-cell-flip')

      const style = {}
      if (isAnimating && cellColor) {
        style['--cell-color'] = cellColor
        style['--col'] = colIndex
      }

      cells.push(
        <div
          key={colIndex}
          className={cellClasses.join(' ')}
          style={Object.keys(style).length > 0 ? style : undefined}
        >
          {letter}
        </div>,
      )
    }

    rows.push(
      <div key={rowIndex} className={rowClasses.join(' ')}>
        {cells}
      </div>,
    )
  }

  return <div className="guess-grid">{rows}</div>
}

export default GuessGrid
