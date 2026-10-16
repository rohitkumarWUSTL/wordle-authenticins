import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import * as gamesApi from '../api/games.js'
import GameDetailPage from './GameDetailPage.jsx'

vi.mock('../api/games.js')

const FLIP_STAGGER_MS = 100
const FLIP_DURATION_MS = 600

function makeGame(overrides = {}) {
  return {
    id: 1,
    status: 'IN_PROGRESS',
    word_length: 5,
    target_word: 'crane',
    guesses: [],
    ...overrides,
  }
}

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

function renderPage() {
  return render(
    <MemoryRouter initialEntries={['/games/1']}>
      <Routes>
        <Route path="/games/:id" element={<GameDetailPage />} />
      </Routes>
    </MemoryRouter>,
  )
}

describe('GameDetailPage', () => {
  let user

  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true })
    // @testing-library/dom's waitFor only takes the fake-timer code path
    // when `jest` is defined. Under Vitest it isn't, so waitFor falls back
    // to real timers and times out. Define a minimal `jest` shim so waitFor
    // can advance the fake clock.
    globalThis.jest = {
      advanceTimersByTime: (ms) => vi.advanceTimersByTime(ms),
    }
    user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
  })

  afterEach(() => {
    cleanup()
    vi.useRealTimers()
    // resetAllMocks (not clearAllMocks) so mock implementations set in one
    // test don't leak into the next.
    vi.resetAllMocks()
    delete globalThis.jest
  })

  it('shows the guess counter while the game is in progress', async () => {
    gamesApi.getGame.mockResolvedValue(makeGame())
    renderPage()
    expect(await screen.findByText('Guess 1 of 6')).toBeInTheDocument()
  })

  it('shows the result banner immediately when loading a finished game', async () => {
    gamesApi.getGame.mockResolvedValue(
      makeGame({
        status: 'WON',
        guesses: [makeGuess('crane', Array(5).fill('GREEN'))],
      }),
    )
    renderPage()
    expect(await screen.findByText('You won! 🎉')).toBeInTheDocument()
  })

  it('shows the target word uppercased on a loss', async () => {
    gamesApi.getGame.mockResolvedValue(
      makeGame({ status: 'LOST', target_word: 'crane' }),
    )
    renderPage()
    expect(await screen.findByText(/the word was CRANE/)).toBeInTheDocument()
  })

  it('keeps the guess counter until the reveal animation finishes, then morphs to the result', async () => {
    gamesApi.getGame.mockResolvedValueOnce(makeGame())
    gamesApi.submitGuess.mockResolvedValue(
      makeGame({
        status: 'WON',
        guesses: [makeGuess('crane', Array(5).fill('GREEN'))],
      }),
    )

    renderPage()
    await screen.findByText('Guess 1 of 6')

    for (const letter of 'crane') {
      await user.click(screen.getByRole('button', { name: letter }))
    }
    await user.click(screen.getByRole('button', { name: 'ENTER' }))

    await waitFor(() => {
      expect(screen.getByText('Guess 2 of 6')).toBeInTheDocument()
    })
    expect(screen.queryByText('You won! 🎉')).not.toBeInTheDocument()

    const revealDelay = 5 * FLIP_STAGGER_MS + FLIP_DURATION_MS
    await vi.advanceTimersByTimeAsync(revealDelay)

    await waitFor(() => {
      expect(screen.getByText('You won! 🎉')).toBeInTheDocument()
    })
  })

  it('recolors the keyboard only after the reveal animation finishes', async () => {
    gamesApi.getGame.mockResolvedValueOnce(makeGame())
    gamesApi.submitGuess.mockResolvedValue(
      makeGame({
        guesses: [makeGuess('crane', Array(5).fill('GREEN'))],
      }),
    )

    renderPage()
    await screen.findByText('Guess 1 of 6')

    for (const letter of 'crane') {
      await user.click(screen.getByRole('button', { name: letter }))
    }
    await user.click(screen.getByRole('button', { name: 'ENTER' }))

    await waitFor(() => {
      expect(screen.getByText('Guess 2 of 6')).toBeInTheDocument()
    })

    expect(screen.getByRole('button', { name: 'c' })).not.toHaveClass(
      'keyboard-key-green',
    )

    const revealDelay = 5 * FLIP_STAGGER_MS + FLIP_DURATION_MS
    await vi.advanceTimersByTimeAsync(revealDelay)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'c' })).toHaveClass(
        'keyboard-key-green',
      )
    })
  })

  it('shows a toast and shakes when the guess is too short', async () => {
    gamesApi.getGame.mockResolvedValue(makeGame())
    renderPage()
    await screen.findByText('Guess 1 of 6')

    await user.click(screen.getByRole('button', { name: 'ENTER' }))

    expect(await screen.findByText('Not enough letters')).toBeInTheDocument()
    expect(gamesApi.submitGuess).not.toHaveBeenCalled()
  })

  it('shows an error message when the game fails to load', async () => {
    gamesApi.getGame.mockRejectedValue(new Error('boom'))
    renderPage()
    expect(await screen.findByText(/Error: boom/)).toBeInTheDocument()
  })
})
