import { useEffect, useState, useRef } from 'react'
import { useParams } from 'react-router-dom'
import api from '@/api/client'

interface LeaderboardEntry {
  rank: number
  user_id: number
  score: number
}

export default function CompetitionDetail() {
  const { id } = useParams<{ id: string }>()
  const [entries, setEntries] = useState<LeaderboardEntry[]>([])
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    api.get(`/competitions/${id}/leaderboard`).then((res) => {
      const mapped = res.data.map((e: any) => ({
        rank: e.rank_position,
        user_id: e.user_id,
        score: e.best_score,
      }))
      setEntries(mapped)
    })

    const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/leaderboard/${id}`)
    wsRef.current = ws
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data)
      if (msg.event === 'update') {
        api.get(`/competitions/${id}/leaderboard`).then((res) => {
          setEntries(res.data.map((e: any) => ({ rank: e.rank_position, user_id: e.user_id, score: e.best_score })))
        })
      }
    }
    return () => ws.close()
  }, [id])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Competition #{id}</h1>
      <h2 className="text-lg font-semibold mb-4">Live Leaderboard</h2>
      <table className="w-full bg-white rounded shadow">
        <thead className="bg-gray-100">
          <tr>
            <th className="px-4 py-2 text-left">Rank</th>
            <th className="px-4 py-2 text-left">User</th>
            <th className="px-4 py-2 text-left">Score</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((e) => (
            <tr key={e.user_id} className="border-t">
              <td className="px-4 py-2">{e.rank}</td>
              <td className="px-4 py-2">User #{e.user_id}</td>
              <td className="px-4 py-2">{e.score?.toFixed(4)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
