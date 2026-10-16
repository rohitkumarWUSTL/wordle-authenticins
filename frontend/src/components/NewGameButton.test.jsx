import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import NewGameButton from './NewGameButton.jsx'

describe('NewGameButton', () => {
  it('renders a + label in the compact variant', () => {
    render(<NewGameButton variant="compact" onCreate={vi.fn()} />)
    expect(screen.getByText('+')).toBeInTheDocument()
  })

  it('renders a "Start new game" label in the full variant', () => {
    render(<NewGameButton variant="full" onCreate={vi.fn()} />)
    expect(screen.getByText('Start new game')).toBeInTheDocument()
  })

  it('offers one option per supported word length', () => {
    render(<NewGameButton variant="full" onCreate={vi.fn()} />)
    // The placeholder option is disabled and hidden, so it is not exposed
    // as an option role. Only the real word-length options are counted.
    const options = screen.getAllByRole('option')
    expect(options).toHaveLength(4)
    expect(
      screen.getByRole('option', { name: 'Word length: 5 letters' }),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('option', { name: 'Word length: 8 letters' }),
    ).toBeInTheDocument()
  })

  it('calls onCreate with the selected word length', async () => {
    const onCreate = vi.fn()
    render(<NewGameButton variant="full" onCreate={onCreate} />)
    await userEvent.selectOptions(
      screen.getByRole('combobox'),
      screen.getByRole('option', { name: 'Word length: 6 letters' }),
    )
    expect(onCreate).toHaveBeenCalledWith(6)
  })

  it('resets the select after a selection so the same option can be reused', async () => {
    const onCreate = vi.fn()
    render(<NewGameButton variant="full" onCreate={onCreate} />)
    const select = screen.getByRole('combobox')
    await userEvent.selectOptions(
      select,
      screen.getByRole('option', { name: 'Word length: 5 letters' }),
    )
    expect(select.value).toBe('')
  })

  it('disables the select when disabled', () => {
    render(<NewGameButton variant="full" onCreate={vi.fn()} disabled />)
    expect(screen.getByRole('combobox')).toBeDisabled()
  })
})
