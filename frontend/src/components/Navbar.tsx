import React from 'react'
import Link from 'next/link'
import { useAuth } from '@/lib/auth-context'
import { useRouter } from 'next/router'

export function Navbar() {
  const { user, logout, isAuthenticated } = useAuth()
  const router = useRouter()

  const handleLogout = async () => {
    await logout()
    router.push('/auth/login')
  }

  return (
    <nav className="bg-gray-900 text-white shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <Link href="/" className="text-2xl font-bold text-red-500">
            StreamBox
          </Link>

          <div className="flex items-center space-x-6">
            <Link href="/" className="hover:text-red-500">
              Home
            </Link>
            <Link href="/movies" className="hover:text-red-500">
              Movies
            </Link>
            <Link href="/tv-shows" className="hover:text-red-500">
              TV Shows
            </Link>
            <Link href="/anime" className="hover:text-red-500">
              Anime
            </Link>

            {isAuthenticated ? (
              <div className="flex items-center space-x-4">
                <Link href="/dashboard" className="hover:text-red-500">
                  Dashboard
                </Link>
                <div className="relative group">
                  <button className="hover:text-red-500">{user?.email}</button>
                  <div className="hidden group-hover:block absolute right-0 mt-2 w-48 bg-gray-800 rounded-lg shadow-lg">
                    <Link href="/profile" className="block px-4 py-2 hover:bg-gray-700">
                      Profile
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 hover:bg-gray-700"
                    >
                      Logout
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex space-x-4">
                <Link
                  href="/auth/login"
                  className="bg-red-500 px-4 py-2 rounded hover:bg-red-600"
                >
                  Login
                </Link>
                <Link
                  href="/auth/register"
                  className="border border-red-500 px-4 py-2 rounded hover:bg-red-500"
                >
                  Register
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
