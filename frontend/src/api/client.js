const host = window.location.hostname

// In GitHub Codespaces the frontend is served from
// https://<codespace>-5173.app.github.dev and the backend is forwarded to
// https://<codespace>-8000.app.github.dev. Rewrite the port so the browser
// reaches the backend instead of its own localhost.
export const API_URL = host.endsWith('.app.github.dev')
  ? `https://${host.replace('-5173.', '-8000.')}`
  : 'http://localhost:8000'

export async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  })

  if (!response.ok) {
    let detail = response.statusText
    try {
      const body = await response.json()
      if (body && body.detail) {
        detail = body.detail
      }
    } catch {
      // ignore JSON parse errors, fall back to statusText
    }
    throw new Error(detail)
  }

  if (response.status === 204) {
    return null
  }

  return response.json()
}
