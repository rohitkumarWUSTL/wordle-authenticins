import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Link, useLocation, useParams } from 'react-router-dom'
import { getGame, giveUp, submitGuess } from '../api/games.js'
import ConfirmModal from '../components/ConfirmModal.jsx'
import GuessGrid from '../components/GuessGrid.jsx'
import Keyboard from '../components/Keyboard.jsx'

const COLOR_RANK = { GREEN: 3, YELLOW: 2, GRAY: 1 }

const FLIP_STAGGER_MS = 100
const FLIP_DURATION_MS = 600
const SHAKE_DURATION_MS = 400
const TOAST_DURATION_MS = 1500

// The first cross-origin request to the backend can fail transiently while
// the dev port forward / TLS cert is still warming up. Retry a few times
// with a short backoff before surfacing the error to the user.
const FETCH_RETRIES = 3
const FETCH_RETRY_DELAY_MS = 500

function isNetworkError(err) {
  // fetch() rejects with a TypeError ("Failed to fetch") for network-level
  // failures. HTTP errors from our client throw a plain Error with a
  // message, so we only retry the former.
  return err instanceof TypeError
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

async function getGameWithRetry(id, isCancelled) {
  let lastError
  for (let attempt = 0; attempt <= FETCH_RETRIES; attempt += 1) {
    if (isCancelled()) throw new Error('cancelled')
    try {
      return await getGame(id)
    } catch (err) {
      lastError = err
      if (!isNetworkError(err) || attempt === FETCH_RETRIES) {
        throw err
      }
      await delay(FETCH_RETRY_DELAY_MS * (attempt + 1))
    }
  }
  throw lastError
}

function GameDetailPage() {
  const { id } = useParams()
  const location = useLocation()
  // Where to return to when the user clicks "Back to games". Falls back to
  // the games list root when the page was opened directly (no state).
  const backTo = location.state?.from ?? '/games'
  const [game, setGame] = useState(null)
  // A snapshot of `game` used for the keyboard colors. It lags behind
  // `game` while the reveal animation is running, so the keyboard doesn't
  // recolor until the flip has finished.
  const [revealedGame, setRevealedGame] = useState(null)
  const [currentGuess, setCurrentGuess] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [toast, setToast] = useState(null)
  const [showGiveUp, setShowGiveUp] = useState(false)
  const [animatingRow, setAnimatingRow] = useState(-1)
  const [shake, setShake] = useState(false)
  const [showResult, setShowResult] = useState(false)

  const toastTimer = useRef(null)
  const animTimer = useRef(null)
  const shakeTimer = useRef(null)
  const resultTimer = useRef(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    setShowResult(false)

    getGameWithRetry(id, () => cancelled)
      .then((data) => {
        if (cancelled) return
        setGame(data)
        setRevealedGame(data)
        // On a fresh load there is no reveal animation to wait for, so
        // show the result immediately if the game is already finished.
        if (data.status !== 'IN_PROGRESS') {
          setShowResult(true)
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
      if (resultTimer.current) clearTimeout(resultTimer.current)
    }
  }, [])

  const isFinished = game ? game.status !== 'IN_PROGRESS' : false
  const wordLength = game ? game.word_length : 0
  const maxGuesses = game ? game.word_length + 1 : 0

  const letterStates = useMemo(() => {
    if (!revealedGame) return {}
    const states = {}
    for (const guess of revealedGame.guesses) {
      for (const item of guess.feedback) {
        const letter = item.letter
        const current = states[letter]
        if (!current || COLOR_RANK[item.color] > COLOR_RANK[current]) {
          states[letter] = item.color
        }
      }
    }
    return states
  }, [revealedGame])

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
      // The guess endpoint returns the full updated game, so there's no
      // need for a follow-up GET.
      const updated = await submitGuess(id, currentGuess)
      const newRowIndex = updated.guesses.length - 1
      // Set the animating row and the new game state in the same batch so
      // the cells render once, with the flip animation already applied.
      setAnimatingRow(newRowIndex)
      setGame(updated)
      setCurrentGuess('')
      const revealDelay = wordLength * FLIP_STAGGER_MS + FLIP_DURATION_MS
      if (animTimer.current) clearTimeout(animTimer.current)
      animTimer.current = setTimeout(() => setAnimatingRow(-1), revealDelay)
      // Delay the keyboard recolor (and the result banner, if the game
      // ended) until the flip reveal has finished.
      if (resultTimer.current) clearTimeout(resultTimer.current)
      resultTimer.current = setTimeout(() => {
        setRevealedGame(updated)
        if (updated.status !== 'IN_PROGRESS') {
          setShowResult(true)
        }
      }, revealDelay)
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
      setRevealedGame(updated)
      setCurrentGuess('')
      setShowResult(true)
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
          <Link to={backTo}>← Back to games</Link>
        </p>
        <p className="games-status">Loading…</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="game-detail-page">
        <p>
          <Link to={backTo}>← Back to games</Link>
        </p>
        <p className="games-status games-error">Error: {error}</p>
      </div>
    )
  }

  if (!game) {
    return null
  }

  // The banner keeps showing "Guess x of y" until the reveal animation
  // finishes, then switches to the result text and color. This avoids both
  // a layout shift and giving the result away early.
  const showResultBanner = isFinished && showResult
  const bannerStatus = showResultBanner ? game.status.toLowerCase() : 'in_progress'
  // Clamp the displayed guess number so the final guess doesn't briefly
  // read "Guess 7 of 6" while the reveal animation is still running.
  const guessNumber = Math.min(game.guesses.length + 1, maxGuesses)

  return (
    <div className="game-detail-page">
      <p>
        <Link to={backTo}>← Back to games</Link>
      </p>
      <h1>Game {game.id}</h1>

      <div className={`game-status-banner game-status-${bannerStatus}`}>
        {showResultBanner && game.status === 'WON' && (
          <span>You won! 🎉</span>
        )}
        {showResultBanner && game.status === 'LOST' && (
          <span>
            You lost — the word was {game.target_word.toUpperCase()}
          </span>
        )}
        {!showResultBanner && (
          <span>
            Guess {guessNumber} of {maxGuesses}
          </span>
        )}
      </div>

      {/* The give-up row is always rendered so its height is reserved even
          after the game ends. Without this, removing it on win/loss would
          shift the board and keyboard up. */}
      <div
        className={`game-give-up-row${
          isFinished ? ' game-give-up-row-hidden' : ''
        }`}
      >
        <button
          type="button"
          className="game-give-up-button"
          onClick={() => setShowGiveUp(true)}
          disabled={submitting || isFinished}
        >
          Give up
        </button>
      </div>

      <div className="game-board">
        <GuessGrid
          guesses={game.guesses}
          wordLength={wordLength}
          maxGuesses={maxGuesses}
          currentGuess={currentGuess}
          animatingRow={animatingRow}
          shake={shake}
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
