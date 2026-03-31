import React, { useEffect } from 'react'
import { useRouter } from 'next/router'
import { useAuth } from '@/lib/auth-context'
import { Navbar } from '@/components/Navbar'

export default function DashboardPage() {
  const { user, isAuthenticated } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/auth/login')
    }
  }, [isAuthenticated, router])

  if (!isAuthenticated || !user) {
    return <div>Loading...</div>
  }

  return (
    <div className="min-h-screen bg-gray-900">
      <Navbar />

      <main className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-white mb-8">Dashboard</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-gray-400 text-sm font-semibold mb-2">Email</h3>
            <p className="text-white text-lg">{user.email}</p>
          </div>

          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-gray-400 text-sm font-semibold mb-2">Username</h3>
            <p className="text-white text-lg">{user.username}</p>
          </div>

          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-gray-400 text-sm font-semibold mb-2">Member Since</h3>
            <p className="text-white text-lg">
              {new Date(user.createdAt).toLocaleDateString()}
            </p>
          </div>

          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-gray-400 text-sm font-semibold mb-2">Role</h3>
            <p className="text-white text-lg capitalize">{user.role}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-gray-800 p-6 rounded-lg">
            <h2 className="text-2xl font-bold text-white mb-4">Continue Watching</h2>
            <p className="text-gray-400">No content in your continue watching list yet.</p>
          </div>

          <div className="bg-gray-800 p-6 rounded-lg">
            <h2 className="text-2xl font-bold text-white mb-4">Watchlist</h2>
            <p className="text-gray-400">Your watchlist is empty. Start adding content!</p>
          </div>
        </div>
      </main>
    </div>
  )
}
