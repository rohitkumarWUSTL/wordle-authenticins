import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getGame, giveUp, submitGuess } from '../api/games.js'
import ConfirmModal from '../components/ConfirmModal.jsx'
import GuessGrid from '../components/GuessGrid.jsx'
import Keyboard from '../components/Keyboard.jsx'

const COLOR_RANK = { GREEN: 3, YELLOW: 2, GRAY: 1 }

const FLIP_STAGGER_MS = 100
const FLIP_DURATION_MS = 600
const BOUNCE_DURATION_MS = 800
const SHAKE_DURATION_MS = 400
const TOAST_DURATION_MS = 1500

function GameDetailPage() {
  const { id } = useParams()
  const [game, setGame] = useState(null)
  const [currentGuess, setCurrentGuess] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [toast, setToast] = useState(null)
  const [showGiveUp, setShowGiveUp] = useState(false)
  const [animatingRow, setAnimatingRow] = useState(-1)
  const [shake, setShake] = useState(false)
  const [showWinBanner, setShowWinBanner] = useState(false)

  const toastTimer = useRef(null)
  const animTimer = useRef(null)
  const shakeTimer = useRef(null)
  const winBannerTimer = useRef(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    setShowWinBanner(false)

    getGame(id)
      .then((data) => {
        if (cancelled) return
        setGame(data)
        // On a fresh load there is no reveal animation to wait for, so
        // show the win banner immediately if the game is already won.
        if (data.status === 'WON') {
          setShowWinBanner(true)
        }
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

  useEffect(() => {
    return () => {
      if (toastTimer.current) clearTimeout(toastTimer.current)
      if (animTimer.current) clearTimeout(animTimer.current)
      if (shakeTimer.current) clearTimeout(shakeTimer.current)
      if (winBannerTimer.current) clearTimeout(winBannerTimer.current)
    }
  }, [])

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

  const showToast = useCallback((message) => {
    setToast(message)
    if (toastTimer.current) clearTimeout(toastTimer.current)
    toastTimer.current = setTimeout(() => setToast(null), TOAST_DURATION_MS)
  }, [])

  const triggerShake = useCallback(() => {
    setShake(true)
    if (shakeTimer.current) clearTimeout(shakeTimer.current)
    shakeTimer.current = setTimeout(() => setShake(false), SHAKE_DURATION_MS)
  }, [])

  const handleKey = useCallback(
    (letter) => {
      if (isFinished || submitting) return
      setCurrentGuess((prev) =>
        prev.length < wordLength ? prev + letter : prev,
      )
    },
    [isFinished, submitting, wordLength],
  )

  const handleBackspace = useCallback(() => {
    if (isFinished || submitting) return
    setCurrentGuess((prev) => prev.slice(0, -1))
  }, [isFinished, submitting])

  const handleEnter = useCallback(async () => {
    if (isFinished || submitting) return
    if (currentGuess.length !== wordLength) {
      showToast('Not enough letters')
      triggerShake()
      return
    }

    setSubmitting(true)
    try {
      await submitGuess(id, currentGuess)
      const updated = await getGame(id)
      const newRowIndex = updated.guesses.length - 1
      // Set the animating row and the new game state in the same batch so
      // the cells render once, with the flip animation already applied.
      setAnimatingRow(newRowIndex)
      setGame(updated)
      setCurrentGuess('')
      if (animTimer.current) clearTimeout(animTimer.current)
      animTimer.current = setTimeout(
        () => setAnimatingRow(-1),
        wordLength * FLIP_STAGGER_MS + FLIP_DURATION_MS,
      )
      // Delay the win banner until after the flip reveal and the bounce
      // animation on the winning row have both finished.
      if (updated.status === 'WON') {
        if (winBannerTimer.current) clearTimeout(winBannerTimer.current)
        winBannerTimer.current = setTimeout(
          () => setShowWinBanner(true),
          wordLength * FLIP_STAGGER_MS +
            FLIP_DURATION_MS +
            BOUNCE_DURATION_MS,
        )
      }
    } catch (err) {
      showToast(err.message)
      triggerShake()
    } finally {
      setSubmitting(false)
    }
  }, [
    currentGuess,
    id,
    isFinished,
    submitting,
    wordLength,
    showToast,
    triggerShake,
  ])

  const handleGiveUpConfirm = useCallback(async () => {
    setShowGiveUp(false)
    setSubmitting(true)
    try {
      const updated = await giveUp(id)
      setGame(updated)
      setCurrentGuess('')
    } catch (err) {
      showToast(err.message)
    } finally {
      setSubmitting(false)
    }
  }, [id, showToast])

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

  const winBannerPending = game.status === 'WON' && !showWinBanner

  return (
    <div className="game-detail-page">
      <p>
        <Link to="/games">← Back to games</Link>
      </p>
      <h1>Game {game.id}</h1>

      <div
        className={`game-status-banner game-status-${game.status.toLowerCase()}${
          winBannerPending ? ' game-status-banner-hidden' : ''
        }`}
      >
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

      {!isFinished && (
        <div className="game-give-up-row">
          <button
            type="button"
            className="game-give-up-button"
            onClick={() => setShowGiveUp(true)}
            disabled={submitting}
          >
            Give up
          </button>
        </div>
      )}

      <div className="game-board">
        <GuessGrid
          guesses={game.guesses}
          wordLength={wordLength}
          maxGuesses={maxGuesses}
          currentGuess={currentGuess}
          animatingRow={animatingRow}
          shake={shake}
          won={game.status === 'WON'}
        />
        {toast && <div className="game-toast">{toast}</div>}
      </div>

      <Keyboard
        onKey={handleKey}
        onEnter={handleEnter}
        onBackspace={handleBackspace}
        letterStates={letterStates}
        disabled={isFinished || submitting}
      />

      <ConfirmModal
        open={showGiveUp}
        title="Give up?"
        message="This will end the game and reveal the answer."
        confirmLabel="Give up"
        cancelLabel="Keep playing"
        danger
        onConfirm={handleGiveUpConfirm}
        onCancel={() => setShowGiveUp(false)}
      />
    </div>
  )
}

export default GameDetailPage
