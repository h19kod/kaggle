import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from '@/context/AuthContext'
import Navbar from '@/components/Navbar'
import Home from '@/pages/Home'
import Datasets from '@/pages/Datasets'
import Notebooks from '@/pages/Notebooks'
import Competitions from '@/pages/Competitions'
import CompetitionDetail from '@/pages/CompetitionDetail'
import Courses from '@/pages/Courses'
import Community from '@/pages/Community'
import Jobs from '@/pages/Jobs'
import Login from '@/pages/Login'

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Navbar />
        <main className="max-w-7xl mx-auto px-6 py-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/datasets" element={<Datasets />} />
            <Route path="/notebooks" element={<Notebooks />} />
            <Route path="/competitions" element={<Competitions />} />
            <Route path="/competitions/:id" element={<CompetitionDetail />} />
            <Route path="/courses" element={<Courses />} />
            <Route path="/community" element={<Community />} />
            <Route path="/jobs" element={<Jobs />} />
            <Route path="/login" element={<Login />} />
          </Routes>
        </main>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
