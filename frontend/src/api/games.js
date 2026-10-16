import { request } from './client.js'
import { STATUS_ALL } from '../constants.js'

export async function listGames({ status, limit, offset }) {
  const params = new URLSearchParams()
  if (status && status !== STATUS_ALL) {
    params.set('status', status)
  }
  params.set('limit', String(limit))
  params.set('offset', String(offset))

  return request(`/games?${params.toString()}`)
}

export async function createGame({ wordLength }) {
  return request('/games', {
    method: 'POST',
    body: JSON.stringify({ word_length: wordLength }),
  })
}

export async function getGame(id) {
  return request(`/games/${id}`)
}

export async function submitGuess(id, word) {
  return request(`/games/${id}/guesses`, {
    method: 'POST',
    body: JSON.stringify({ word }),
  })
}

export async function giveUp(id) {
  return request(`/games/${id}/give-up`, {
    method: 'POST',
  })
}
