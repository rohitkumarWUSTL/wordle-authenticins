import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import Pagination from './Pagination.jsx'

describe('Pagination', () => {
  it('disables Previous on the first page', () => {
    render(
      <Pagination total={100} limit={20} offset={0} onChange={vi.fn()} />,
    )
    expect(screen.getByRole('button', { name: /previous/i })).toBeDisabled()
  })

  it('disables Next on the last page', () => {
    render(
      <Pagination total={100} limit={20} offset={80} onChange={vi.fn()} />,
    )
    expect(screen.getByRole('button', { name: /next/i })).toBeDisabled()
  })

  it('calls onChange with the previous offset', async () => {
    const onChange = vi.fn()
    render(
      <Pagination total={100} limit={20} offset={40} onChange={onChange} />,
    )
    await userEvent.click(screen.getByRole('button', { name: /previous/i }))
    expect(onChange).toHaveBeenCalledWith(20)
  })

  it('calls onChange with the next offset', async () => {
    const onChange = vi.fn()
    render(
      <Pagination total={100} limit={20} offset={40} onChange={onChange} />,
    )
    await userEvent.click(screen.getByRole('button', { name: /next/i }))
    expect(onChange).toHaveBeenCalledWith(60)
  })
})
