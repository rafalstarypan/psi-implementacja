import { Link, useLocation, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '@/features/auth/AuthContext'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { PawPrint, Package, Stethoscope, LogOut, User, Home } from 'lucide-react'

export function Layout() {
  const { user, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()

  const navigation = [
    {
      name: 'Zaopatrzenie',
      href: '/panel/supplies',
      icon: Package,
    },
    {
      name: 'Historia zdrowia',
      href: '/panel/animals',
      icon: Stethoscope,
    },
  ]

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <Link to="/" className="flex items-center space-x-3 hover:opacity-80">
                <PawPrint className="h-8 w-8 text-primary" />
                <span className="text-xl font-bold text-gray-900">
                  System Schroniska
                </span>
              </Link>
            </div>

            <nav className="hidden md:flex space-x-1">
              <Link
                to="/"
                className="flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-colors"
              >
                <Home className="h-4 w-4" />
                <span>Strona główna</span>
              </Link>
              {navigation.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname.startsWith(item.href)
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={cn(
                      'flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-gray-900 text-white'
                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{item.name}</span>
                  </Link>
                )
              })}
            </nav>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <User className="h-4 w-4" />
                <span>{user?.full_name}</span>
                <span className="text-gray-400">|</span>
                <span className="text-primary font-medium">{user?.role_display}</span>
              </div>
              <Button variant="ghost" size="sm" onClick={handleLogout}>
                <LogOut className="h-4 w-4 mr-2" />
                Wyloguj
              </Button>
            </div>
          </div>
        </div>

        {/* Mobile navigation */}
        <nav className="md:hidden border-t px-4 py-2 flex space-x-2">
          {navigation.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname.startsWith(item.href)
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  'flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium flex-1 justify-center',
                  isActive
                    ? 'bg-gray-900 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                )}
              >
                <Icon className="h-4 w-4" />
                <span>{item.name}</span>
              </Link>
            )
          })}
        </nav>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  )
}
