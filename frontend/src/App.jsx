import { Navigate, Route, Routes } from 'react-router-dom'
import './App.css'
import GamesPage from './pages/GamesPage.jsx'
import GameDetailPage from './pages/GameDetailPage.jsx'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/games" replace />} />
      <Route path="/games" element={<GamesPage />} />
      <Route path="/games/:id" element={<GameDetailPage />} />
    </Routes>
  )
}

export default App
