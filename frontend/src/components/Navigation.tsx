import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../lib/auth'

export default function Navigation() {
  const { user, logout } = useAuth()
  const location = useLocation()

  const isActive = (path: string) => location.pathname === path

  return (
    <nav className="bg-white border-b sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="text-2xl">👖</div>
            <span className="text-xl font-bold text-indigo-600">Vintage Jeans</span>
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-8">
            <Link
              to="/blog"
              className={`text-sm font-medium transition-colors ${
                isActive('/blog') ? 'text-indigo-600' : 'text-gray-700 hover:text-indigo-600'
              }`}
            >
              Blog
            </Link>
            <Link
              to="/sell"
              className={`text-sm font-medium transition-colors ${
                isActive('/sell') ? 'text-indigo-600' : 'text-gray-700 hover:text-indigo-600'
              }`}
            >
              Sell Jeans
            </Link>

            {user ? (
              <>
                <Link
                  to={user.role === 'admin' ? '/admin/dashboard' : '/seller/dashboard'}
                  className="text-sm font-medium text-gray-700 hover:text-indigo-600 transition-colors"
                >
                  Dashboard
                </Link>
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-600">Hi, {user.full_name.split(' ')[0]}</span>
                  <button
                    onClick={logout}
                    className="text-sm font-medium text-gray-700 hover:text-indigo-600 transition-colors"
                  >
                    Logout
                  </button>
                </div>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-sm font-medium text-gray-700 hover:text-indigo-600 transition-colors"
                >
                  Log in
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 transition-colors shadow-sm"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button className="text-gray-700 hover:text-indigo-600">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}
