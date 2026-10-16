import { render } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

// Renders `ui` inside a MemoryRouter. Pass `path` and `route` to mount the
// component at a specific route (useful for pages that read useParams).
export function renderWithRouter(
  ui,
  { route = '/', path = '*', initialEntries } = {},
) {
  const entries = initialEntries ?? [route]
  return render(
    <MemoryRouter initialEntries={entries}>
      <Routes>
        <Route path={path} element={ui} />
      </Routes>
    </MemoryRouter>,
  )
}
