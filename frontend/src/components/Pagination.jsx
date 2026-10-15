function Pagination({ total, limit, offset, onChange }) {
  const totalPages = Math.max(1, Math.ceil(total / limit))
  const currentPage = Math.floor(offset / limit) + 1

  const canPrev = offset > 0
  const canNext = offset + limit < total

  return (
    <nav className="pagination" aria-label="Pagination">
      <button
        type="button"
        onClick={() => onChange(Math.max(0, offset - limit))}
        disabled={!canPrev}
      >
        Previous
      </button>
      <span className="pagination-status">
        Page {currentPage} of {totalPages}
      </span>
      <button
        type="button"
        onClick={() => onChange(offset + limit)}
        disabled={!canNext}
      >
        Next
      </button>
    </nav>
  )
}

export default Pagination
