import React from 'react'
import Image from 'next/image'
import Link from 'next/link'

interface ContentCardProps {
  id: number
  title: string
  posterUrl?: string
  rating?: number
  contentType: string
}

export function ContentCard({ id, title, posterUrl, rating, contentType }: ContentCardProps) {
  return (
    <Link href={`/watch/${id}`}>
      <div className="relative group cursor-pointer">
        <div className="relative w-full aspect-video bg-gray-800 rounded-lg overflow-hidden">
          {posterUrl ? (
            <Image
              src={posterUrl}
              alt={title}
              fill
              className="object-cover group-hover:scale-110 transition-transform duration-300"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <span className="text-gray-500">No Image</span>
            </div>
          )}
        </div>
        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-70 transition-all duration-300 rounded-lg flex flex-col justify-end p-4 opacity-0 group-hover:opacity-100">
          <h3 className="text-white font-bold">{title}</h3>
          {rating && <p className="text-yellow-500">★ {rating.toFixed(1)}</p>}
        </div>
      </div>
    </Link>
  )
}
