import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getGame, submitGuess } from '../api/games.js'
import GuessGrid from '../components/GuessGrid.jsx'
import Keyboard from '../components/Keyboard.jsx'

const COLOR_RANK = { GREEN: 3, YELLOW: 2, GRAY: 1 }

function GameDetailPage() {
  const { id } = useParams()
  const [game, setGame] = useState(null)
  const [currentGuess, setCurrentGuess] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [guessError, setGuessError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    getGame(id)
      .then((data) => {
        if (cancelled) return
        setGame(data)
      })
      .catch((err) => {
        if (cancelled) return
        setError(err.message)
      })
      .finally(() => {
        if (cancelled) return
        setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [id])

  const isFinished = game ? game.status !== 'IN_PROGRESS' : false
  const wordLength = game ? game.word_length : 0
  const maxGuesses = game ? game.word_length + 1 : 0

  const letterStates = useMemo(() => {
    if (!game) return {}
    const states = {}
    for (const guess of game.guesses) {
      for (const item of guess.feedback) {
        const letter = item.letter
        const current = states[letter]
        if (!current || COLOR_RANK[item.color] > COLOR_RANK[current]) {
          states[letter] = item.color
        }
      }
    }
    return states
  }, [game])

  const handleKey = useCallback(
    (letter) => {
      if (isFinished || submitting) return
      setGuessError(null)
      setCurrentGuess((prev) =>
        prev.length < wordLength ? prev + letter : prev,
      )
    },
    [isFinished, submitting, wordLength],
  )

  const handleBackspace = useCallback(() => {
    if (isFinished || submitting) return
    setGuessError(null)
    setCurrentGuess((prev) => prev.slice(0, -1))
  }, [isFinished, submitting])

  const handleEnter = useCallback(async () => {
    if (isFinished || submitting) return
    if (currentGuess.length !== wordLength) {
      setGuessError(`Guess must be ${wordLength} letters`)
      return
    }

    setSubmitting(true)
    setGuessError(null)
    try {
      await submitGuess(id, currentGuess)
      const updated = await getGame(id)
      setGame(updated)
      setCurrentGuess('')
    } catch (err) {
      setGuessError(err.message)
    } finally {
      setSubmitting(false)
    }
  }, [currentGuess, id, isFinished, submitting, wordLength])

  useEffect(() => {
    const onKeyDown = (event) => {
      if (event.metaKey || event.ctrlKey || event.altKey) return
      const key = event.key
      if (key === 'Enter') {
        event.preventDefault()
        handleEnter()
      } else if (key === 'Backspace') {
        event.preventDefault()
        handleBackspace()
      } else if (/^[a-zA-Z]$/.test(key)) {
        handleKey(key.toLowerCase())
      }
    }

    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [handleEnter, handleBackspace, handleKey])

  if (loading) {
    return (
      <div className="game-detail-page">
        <p>
          <Link to="/games">← Back to games</Link>
        </p>
        <p className="games-status">Loading…</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="game-detail-page">
        <p>
          <Link to="/games">← Back to games</Link>
        </p>
        <p className="games-status games-error">Error: {error}</p>
      </div>
    )
  }

  if (!game) {
    return null
  }

  return (
    <div className="game-detail-page">
      <p>
        <Link to="/games">← Back to games</Link>
      </p>
      <h1>Game {game.id}</h1>

      <div className={`game-status-banner game-status-${game.status.toLowerCase()}`}>
        {game.status === 'WON' && <span>You won! 🎉</span>}
        {game.status === 'LOST' && (
          <span>You lost — the word was {game.target_word}</span>
        )}
        {game.status === 'IN_PROGRESS' && (
          <span>
            Guess {game.guesses.length + 1} of {maxGuesses}
          </span>
        )}
      </div>

      <GuessGrid
        guesses={game.guesses}
        wordLength={wordLength}
        maxGuesses={maxGuesses}
        currentGuess={currentGuess}
      />

      {guessError && <p className="game-guess-error">{guessError}</p>}

      <Keyboard
        onKey={handleKey}
        onEnter={handleEnter}
        onBackspace={handleBackspace}
        letterStates={letterStates}
        disabled={isFinished || submitting}
      />
    </div>
  )
}

export default GameDetailPage
