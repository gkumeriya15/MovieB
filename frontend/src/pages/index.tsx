import React, { useEffect } from 'react'
import { useRouter } from 'next/router'
import { useAuth } from '@/lib/auth-context'
import apiClient from '@/lib/api'
import { useContentStore } from '@/lib/store'
import { Navbar } from '@/components/Navbar'
import { ContentCard } from '@/components/ContentCard'

export default function Home() {
  const { isAuthenticated } = useAuth()
  const { featuredContent, setFeaturedContent, trendingContent, setTrendingContent } = useContentStore()
  const router = useRouter()

  useEffect(() => {
    loadContent()
  }, [])

  const loadContent = async () => {
    try {
      const [featured, trending] = await Promise.all([
        apiClient.getFeaturedContent(10),
        apiClient.getTrendingContent(20),
      ])
      setFeaturedContent(featured.data)
      setTrendingContent(trending.data)
    } catch (error) {
      console.error('Failed to load content:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900">
      <Navbar />

      <main className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <section className="mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">Welcome to StreamBox</h1>
          <p className="text-xl text-gray-300 mb-6">
            Stream movies, TV shows, anime, and live content from around the world
          </p>
          {!isAuthenticated && (
            <button
              onClick={() => router.push('/auth/register')}
              className="bg-red-500 text-white px-8 py-3 rounded-lg hover:bg-red-600 text-lg"
            >
              Start Streaming Free
            </button>
          )}
        </section>

        {/* Featured Content */}
        {featuredContent.length > 0 && (
          <section className="mb-12">
            <h2 className="text-3xl font-bold text-white mb-6">Featured</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
              {featuredContent.map((content) => (
                <ContentCard
                  key={content.id}
                  id={content.id}
                  title={content.title}
                  posterUrl={content.poster_url}
                  rating={content.rating}
                  contentType={content.content_type}
                />
              ))}
            </div>
          </section>
        )}

        {/* Trending Content */}
        {trendingContent.length > 0 && (
          <section className="mb-12">
            <h2 className="text-3xl font-bold text-white mb-6">Trending Now</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
              {trendingContent.slice(0, 10).map((content) => (
                <ContentCard
                  key={content.id}
                  id={content.id}
                  title={content.title}
                  posterUrl={content.poster_url}
                  rating={content.rating}
                  contentType={content.content_type}
                />
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  )
}
