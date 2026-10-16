import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import StatusFilter from './StatusFilter.jsx'

describe('StatusFilter', () => {
  it('renders the current value', () => {
    render(<StatusFilter value="ALL" onChange={vi.fn()} />)
    expect(screen.getByRole('combobox')).toHaveValue('ALL')
  })

  it('calls onChange with the selected value', async () => {
    const onChange = vi.fn()
    render(<StatusFilter value="ALL" onChange={onChange} />)
    await userEvent.selectOptions(
      screen.getByRole('combobox'),
      'IN_PROGRESS',
    )
    expect(onChange).toHaveBeenCalledWith('IN_PROGRESS')
  })
})
