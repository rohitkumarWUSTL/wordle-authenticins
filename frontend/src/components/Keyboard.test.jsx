import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import Keyboard from './Keyboard.jsx'

describe('Keyboard', () => {
  it('renders a key for every letter plus ENTER and BACKSPACE', () => {
    render(
      <Keyboard
        onKey={vi.fn()}
        onEnter={vi.fn()}
        onBackspace={vi.fn()}
        letterStates={{}}
      />,
    )
    expect(screen.getByRole('button', { name: 'ENTER' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'BACKSPACE' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'a' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'z' })).toBeInTheDocument()
  })

  it('calls onKey with the letter when a letter key is clicked', async () => {
    const onKey = vi.fn()
    render(
      <Keyboard
        onKey={onKey}
        onEnter={vi.fn()}
        onBackspace={vi.fn()}
        letterStates={{}}
      />,
    )
    await userEvent.click(screen.getByRole('button', { name: 'a' }))
    expect(onKey).toHaveBeenCalledWith('a')
  })

  it('calls onEnter when ENTER is clicked', async () => {
    const onEnter = vi.fn()
    render(
      <Keyboard
        onKey={vi.fn()}
        onEnter={onEnter}
        onBackspace={vi.fn()}
        letterStates={{}}
      />,
    )
    await userEvent.click(screen.getByRole('button', { name: 'ENTER' }))
    expect(onEnter).toHaveBeenCalled()
  })

  it('calls onBackspace when BACKSPACE is clicked', async () => {
    const onBackspace = vi.fn()
    render(
      <Keyboard
        onKey={vi.fn()}
        onEnter={vi.fn()}
        onBackspace={onBackspace}
        letterStates={{}}
      />,
    )
    await userEvent.click(screen.getByRole('button', { name: 'BACKSPACE' }))
    expect(onBackspace).toHaveBeenCalled()
  })

  it('applies the state class to keys with a known state', () => {
    render(
      <Keyboard
        onKey={vi.fn()}
        onEnter={vi.fn()}
        onBackspace={vi.fn()}
        letterStates={{ a: 'GREEN', b: 'YELLOW', c: 'GRAY' }}
      />,
    )
    expect(screen.getByRole('button', { name: 'a' })).toHaveClass(
      'keyboard-key-green',
    )
    expect(screen.getByRole('button', { name: 'b' })).toHaveClass(
      'keyboard-key-yellow',
    )
    expect(screen.getByRole('button', { name: 'c' })).toHaveClass(
      'keyboard-key-gray',
    )
  })

  it('does not call handlers when disabled', async () => {
    const onKey = vi.fn()
    const onEnter = vi.fn()
    render(
      <Keyboard
        onKey={onKey}
        onEnter={onEnter}
        onBackspace={vi.fn()}
        letterStates={{}}
        disabled
      />,
    )
    await userEvent.click(screen.getByRole('button', { name: 'a' }))
    await userEvent.click(screen.getByRole('button', { name: 'ENTER' }))
    expect(onKey).not.toHaveBeenCalled()
    expect(onEnter).not.toHaveBeenCalled()
  })
})
