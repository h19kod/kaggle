import { useEffect, useState } from 'react'
import api from '@/api/client'

interface Notebook {
  id: number
  title: string
  description: string
  programming_language: string
  total_upvotes: number
}

export default function Notebooks() {
  const [notebooks, setNotebooks] = useState<Notebook[]>([])

  useEffect(() => {
    api.get('/notebooks/').then((res) => setNotebooks(res.data))
  }, [])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Notebooks</h1>
      <div className="grid gap-4">
        {notebooks.map((n) => (
          <div key={n.id} className="bg-white p-4 rounded shadow">
            <h3 className="font-semibold">{n.title}</h3>
            <p className="text-sm text-gray-600">{n.description}</p>
            <div className="text-xs text-gray-400 mt-2">
              {n.programming_language} | Upvotes: {n.total_upvotes}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
