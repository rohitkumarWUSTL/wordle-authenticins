import { useEffect, useRef } from 'react'

function ConfirmModal({
  open,
  title,
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  danger = false,
  onConfirm,
  onCancel,
}) {
  const dialogRef = useRef(null)

  useEffect(() => {
    const dialog = dialogRef.current
    if (!dialog) return

    if (open && !dialog.open) {
      dialog.showModal()
    } else if (!open && dialog.open) {
      dialog.close()
    }
  }, [open])

  const handleBackdropClick = (event) => {
    if (event.target === dialogRef.current) {
      onCancel()
    }
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    onConfirm()
  }

  return (
    <dialog
      ref={dialogRef}
      className="confirm-modal"
      onClose={onCancel}
      onClick={handleBackdropClick}
    >
      <form className="confirm-form" onSubmit={handleSubmit}>
        <h2>{title}</h2>
        {message && <p className="confirm-message">{message}</p>}

        <div className="confirm-actions">
          <button
            type="button"
            className="confirm-cancel"
            onClick={onCancel}
          >
            {cancelLabel}
          </button>
          <button
            type="submit"
            className={`confirm-submit ${danger ? 'confirm-submit-danger' : ''}`.trim()}
          >
            {confirmLabel}
          </button>
        </div>
      </form>
    </dialog>
  )
}

export default ConfirmModal
