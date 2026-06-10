import { useEffect, useState } from 'react'
import api from '@/api/client'

interface Dataset {
  id: number
  title: string
  slug: string
  description: string
  total_views: number
  total_downloads: number
}

export default function Datasets() {
  const [datasets, setDatasets] = useState<Dataset[]>([])

  useEffect(() => {
    api.get('/datasets/').then((res) => setDatasets(res.data))
  }, [])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Datasets</h1>
      <div className="grid gap-4">
        {datasets.map((d) => (
          <div key={d.id} className="bg-white p-4 rounded shadow">
            <h3 className="font-semibold">{d.title}</h3>
            <p className="text-sm text-gray-600">{d.description}</p>
            <div className="text-xs text-gray-400 mt-2">
              Views: {d.total_views} | Downloads: {d.total_downloads}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
