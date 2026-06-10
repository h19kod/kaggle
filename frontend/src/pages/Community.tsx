import { useEffect, useState } from 'react'
import api from '@/api/client'

interface Post {
  id: number
  title: string
  body_content: string
  category: string
  upvotes_count: number
}

export default function Community() {
  const [posts, setPosts] = useState<Post[]>([])

  useEffect(() => {
    api.get('/community/').then((res) => setPosts(res.data))
  }, [])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Community</h1>
      <div className="grid gap-4">
        {posts.map((p) => (
          <div key={p.id} className="bg-white p-4 rounded shadow">
            <div className="text-xs text-blue-600 font-medium uppercase mb-1">{p.category}</div>
            <h3 className="font-semibold">{p.title}</h3>
            <p className="text-sm text-gray-600">{p.body_content}</p>
            <div className="text-xs text-gray-400 mt-2">Upvotes: {p.upvotes_count}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
