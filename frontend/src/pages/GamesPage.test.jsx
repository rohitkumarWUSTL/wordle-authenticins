import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as gamesApi from '../api/games.js'
import GamesPage from './GamesPage.jsx'

vi.mock('../api/games.js')

function renderPage(initialEntries = ['/games']) {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <Routes>
        <Route path="/games" element={<GamesPage />} />
        <Route path="/games/:id" element={<div>Game detail</div>} />
      </Routes>
    </MemoryRouter>,
  )
}

describe('GamesPage', () => {
  afterEach(() => {
    vi.clearAllMocks()
  })

  it('lists games returned by the API', async () => {
    gamesApi.listGames.mockResolvedValue({
      items: [
        { id: 1, status: 'IN_PROGRESS', word_length: 5, guesses: [] },
        { id: 2, status: 'WON', word_length: 5, guesses: [] },
      ],
      total: 2,
    })
    renderPage()
    expect(await screen.findByText('Game 1')).toBeInTheDocument()
    expect(screen.getByText('Game 2')).toBeInTheDocument()
  })

  it('reads the status filter from the URL', async () => {
    gamesApi.listGames.mockResolvedValue({ items: [], total: 0 })
    renderPage(['/games?status=IN_PROGRESS'])
    await waitFor(() => {
      expect(gamesApi.listGames).toHaveBeenCalledWith(
        expect.objectContaining({ status: 'IN_PROGRESS' }),
      )
    })
  })

  it('reads the offset from the URL', async () => {
    gamesApi.listGames.mockResolvedValue({ items: [], total: 0 })
    renderPage(['/games?offset=40'])
    await waitFor(() => {
      expect(gamesApi.listGames).toHaveBeenCalledWith(
        expect.objectContaining({ offset: 40 }),
      )
    })
  })

  it('shows the empty state when there are no games and no filter', async () => {
    gamesApi.listGames.mockResolvedValue({ items: [], total: 0 })
    renderPage()
    expect(await screen.findByText('Start new game')).toBeInTheDocument()
  })

  it('shows the filtered-empty message when a filter yields no games', async () => {
    gamesApi.listGames.mockResolvedValue({ items: [], total: 0 })
    renderPage(['/games?status=IN_PROGRESS'])
    expect(
      await screen.findByText('No games match this filter.'),
    ).toBeInTheDocument()
  })

  it('creates a game and navigates to it', async () => {
    gamesApi.listGames.mockResolvedValue({ items: [], total: 0 })
    gamesApi.createGame.mockResolvedValue({ id: 7 })
    renderPage()
    await screen.findByText('Start new game')

    await userEvent.selectOptions(
      screen.getByRole('combobox', { name: 'Start new game' }),
      screen.getByRole('option', { name: 'Word length: 5 letters' }),
    )

    await waitFor(() => {
      expect(gamesApi.createGame).toHaveBeenCalledWith({ wordLength: 5 })
    })
    expect(await screen.findByText('Game detail')).toBeInTheDocument()
  })
})
