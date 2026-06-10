import { Link } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()

  return (
    <nav className="bg-blue-700 text-white px-6 py-3 shadow-md">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <Link to="/" className="text-xl font-bold">Kaggle Platform</Link>
        <div className="flex gap-6 text-sm">
          <Link to="/datasets" className="hover:underline">Datasets</Link>
          <Link to="/notebooks" className="hover:underline">Notebooks</Link>
          <Link to="/competitions" className="hover:underline">Competitions</Link>
          <Link to="/courses" className="hover:underline">Courses</Link>
          <Link to="/community" className="hover:underline">Community</Link>
          <Link to="/jobs" className="hover:underline">Jobs</Link>
          {user ? (
            <div className="flex gap-4 items-center">
              <span className="font-medium">{user.username}</span>
              <button onClick={logout} className="hover:underline">Logout</button>
            </div>
          ) : (
            <Link to="/login" className="hover:underline">Login</Link>
          )}
        </div>
      </div>
    </nav>
  )
}
