export const MIN_WORD_LENGTH = 5
export const MAX_WORD_LENGTH = 8

export const WORD_LENGTHS = Array.from(
  { length: MAX_WORD_LENGTH - MIN_WORD_LENGTH + 1 },
  (_, i) => MIN_WORD_LENGTH + i,
)

export const PAGE_SIZE = 20

export const STATUS_ALL = 'ALL'
export const STATUS_IN_PROGRESS = 'IN_PROGRESS'
