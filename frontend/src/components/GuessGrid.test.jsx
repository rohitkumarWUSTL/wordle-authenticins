import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import GuessGrid from './GuessGrid.jsx'

function makeGuess(word, colors) {
  return {
    word,
    feedback: word.split('').map((letter, index) => ({
      index,
      letter,
      color: colors[index],
    })),
  }
}

describe('GuessGrid', () => {
  it('renders one row per allowed guess', () => {
    const { container } = render(
      <GuessGrid
        guesses={[]}
        wordLength={5}
        maxGuesses={6}
        currentGuess=""
      />,
    )
    expect(container.querySelectorAll('.guess-row')).toHaveLength(6)
  })

  it('renders one cell per letter in each row', () => {
    const { container } = render(
      <GuessGrid
        guesses={[]}
        wordLength={5}
        maxGuesses={6}
        currentGuess=""
      />,
    )
    const firstRow = container.querySelector('.guess-row')
    expect(firstRow.querySelectorAll('.guess-cell')).toHaveLength(5)
  })

  it('shows the current guess in the active row', () => {
    render(
      <GuessGrid
        guesses={[]}
        wordLength={5}
        maxGuesses={6}
        currentGuess="crane"
      />,
    )
    const cells = screen.getAllByText(/[a-z]/i)
    const letters = cells.map((c) => c.textContent).join('')
    expect(letters).toContain('crane')
  })

  it('applies the color class to a revealed guess', () => {
    const guess = makeGuess('crane', [
      'GREEN',
      'YELLOW',
      'GRAY',
      'GRAY',
      'GRAY',
    ])
    const { container } = render(
      <GuessGrid
        guesses={[guess]}
        wordLength={5}
        maxGuesses={6}
        currentGuess=""
      />,
    )
    expect(container.querySelectorAll('.guess-cell-green')).toHaveLength(1)
    expect(container.querySelectorAll('.guess-cell-yellow')).toHaveLength(1)
    expect(container.querySelectorAll('.guess-cell-gray')).toHaveLength(3)
  })

  it('does not apply color classes to the animating row', () => {
    const guess = makeGuess('crane', [
      'GREEN',
      'GREEN',
      'GREEN',
      'GREEN',
      'GREEN',
    ])
    const { container } = render(
      <GuessGrid
        guesses={[guess]}
        wordLength={5}
        maxGuesses={6}
        currentGuess=""
        animatingRow={0}
      />,
    )
    expect(container.querySelectorAll('.guess-cell-green')).toHaveLength(0)
    expect(container.querySelectorAll('.guess-cell-flip')).toHaveLength(5)
  })

  it('sets the --cell-color and --col variables on animating cells', () => {
    const guess = makeGuess('crane', [
      'GREEN',
      'YELLOW',
      'GRAY',
      'GRAY',
      'GRAY',
    ])
    const { container } = render(
      <GuessGrid
        guesses={[guess]}
        wordLength={5}
        maxGuesses={6}
        currentGuess=""
        animatingRow={0}
      />,
    )
    const firstCell = container.querySelector('.guess-cell-flip')
    expect(firstCell.style.getPropertyValue('--cell-color')).toBe('#6ca965')
    expect(firstCell.style.getPropertyValue('--col')).toBe('0')
  })

  it('adds the shake class to the active row when shake is true', () => {
    const { container } = render(
      <GuessGrid
        guesses={[]}
        wordLength={5}
        maxGuesses={6}
        currentGuess=""
        shake
      />,
    )
    expect(container.querySelectorAll('.guess-row-shake')).toHaveLength(1)
  })
})
