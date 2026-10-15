import { useEffect, useRef, useState } from 'react'
import { MIN_WORD_LENGTH, WORD_LENGTHS } from '../constants.js'

function NewGameModal({ open, onClose, onCreate }) {
  const dialogRef = useRef(null)
  const [wordLength, setWordLength] = useState(MIN_WORD_LENGTH)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    const dialog = dialogRef.current
    if (!dialog) return

    if (open && !dialog.open) {
      setWordLength(MIN_WORD_LENGTH)
      setSubmitting(false)
      setError(null)
      dialog.showModal()
    } else if (!open && dialog.open) {
      dialog.close()
    }
  }, [open])

  const handleBackdropClick = (event) => {
    if (event.target === dialogRef.current) {
      onClose()
    }
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      await onCreate(wordLength)
    } catch (err) {
      setError(err.message)
      setSubmitting(false)
    }
  }

  return (
    <dialog
      ref={dialogRef}
      className="new-game-modal"
      onClose={onClose}
      onClick={handleBackdropClick}
    >
      <form className="new-game-form" onSubmit={handleSubmit}>
        <h2>Start new game</h2>

        <fieldset className="new-game-length">
          <legend>Word length</legend>
          {WORD_LENGTHS.map((length) => (
            <label key={length} className="new-game-length-option">
              <input
                type="radio"
                name="word_length"
                value={length}
                checked={wordLength === length}
                onChange={() => setWordLength(length)}
              />
              {length}
            </label>
          ))}
        </fieldset>

        {error && <p className="new-game-error">Error: {error}</p>}

        <div className="new-game-actions">
          <button
            type="button"
            className="new-game-cancel"
            onClick={onClose}
            disabled={submitting}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="new-game-submit"
            disabled={submitting}
          >
            {submitting ? 'Creating…' : 'Create'}
          </button>
        </div>
      </form>
    </dialog>
  )
}

export default NewGameModal
