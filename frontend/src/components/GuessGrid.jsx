const COLOR_CLASS = {
  GREEN: 'guess-cell-green',
  YELLOW: 'guess-cell-yellow',
  GRAY: 'guess-cell-gray',
}

function GuessGrid({ guesses, wordLength, maxGuesses, currentGuess }) {
  const rows = []

  for (let rowIndex = 0; rowIndex < maxGuesses; rowIndex += 1) {
    const guess = guesses[rowIndex]
    const cells = []

    for (let colIndex = 0; colIndex < wordLength; colIndex += 1) {
      let letter = ''
      let colorClass = ''

      if (guess) {
        const item = guess.feedback[colIndex]
        letter = item ? item.letter : ''
        colorClass = item ? COLOR_CLASS[item.color] || '' : ''
      } else if (rowIndex === guesses.length) {
        letter = currentGuess[colIndex] || ''
        colorClass = letter ? 'guess-cell-active' : ''
      }

      cells.push(
        <div
          key={colIndex}
          className={`guess-cell ${colorClass}`.trim()}
        >
          {letter}
        </div>,
      )
    }

    rows.push(
      <div key={rowIndex} className="guess-row">
        {cells}
      </div>,
    )
  }

  return <div className="guess-grid">{rows}</div>
}

export default GuessGrid
