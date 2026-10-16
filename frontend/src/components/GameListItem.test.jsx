import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { renderWithRouter } from '../test/renderWithRouter.jsx'
import GameListItem from './GameListItem.jsx'

function makeGame(overrides = {}) {
  return {
    id: 1,
    status: 'IN_PROGRESS',
    word_length: 5,
    guesses: [],
    ...overrides,
  }
}

describe('GameListItem', () => {
  it('shows the game id and status label', () => {
    renderWithRouter(<GameListItem game={makeGame()} />)
    expect(screen.getByText('Game 1')).toBeInTheDocument()
    expect(screen.getByText('In progress')).toBeInTheDocument()
  })

  it('shows the guess count out of the allowed total', () => {
    const game = makeGame({
      guesses: [
        { word: 'crane', feedback: [] },
        { word: 'slate', feedback: [] },
      ],
    })
    renderWithRouter(<GameListItem game={game} />)
    expect(screen.getByText('2 / 6')).toBeInTheDocument()
  })

  it('shows a dash when there are no guesses', () => {
    renderWithRouter(<GameListItem game={makeGame()} />)
    expect(screen.getByText('—')).toBeInTheDocument()
  })

  it('renders the last guess feedback as small cells', () => {
    const game = makeGame({
      guesses: [
        {
          word: 'crane',
          feedback: 'crane'.split('').map((letter, index) => ({
            index,
            letter,
            color: 'GREEN',
          })),
        },
      ],
    })
    const { container } = renderWithRouter(<GameListItem game={game} />)
    expect(container.querySelectorAll('.guess-cell-small')).toHaveLength(5)
    expect(container.querySelectorAll('.guess-cell-green')).toHaveLength(5)
  })

  it('links to the game detail page', () => {
    renderWithRouter(<GameListItem game={makeGame({ id: 42 })} />)
    expect(screen.getByRole('link')).toHaveAttribute('href', '/games/42')
  })
})
