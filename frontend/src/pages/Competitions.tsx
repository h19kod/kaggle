import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '@/api/client'

interface Competition {
  id: number
  title: string
  status: string
  evaluation_metric: string
  prize_pool_amount: string
}

export default function Competitions() {
  const [competitions, setCompetitions] = useState<Competition[]>([])

  useEffect(() => {
    api.get('/competitions/').then((res) => setCompetitions(res.data))
  }, [])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Competitions</h1>
      <div className="grid gap-4">
        {competitions.map((c) => (
          <Link key={c.id} to={`/competitions/${c.id}`} className="bg-white p-4 rounded shadow hover:bg-gray-50">
            <h3 className="font-semibold">{c.title}</h3>
            <p className="text-sm text-gray-600">{c.evaluation_metric}</p>
            <div className="text-xs text-gray-400 mt-2">
              Status: {c.status} | Prize: ${c.prize_pool_amount}
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
