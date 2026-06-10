import { useEffect, useState } from 'react'
import api from '@/api/client'

interface Job {
  id: number
  company_name: string
  job_title: string
  description: string
  required_tier_level: string
}

export default function Jobs() {
  const [jobs, setJobs] = useState<Job[]>([])

  useEffect(() => {
    api.get('/jobs/').then((res) => setJobs(res.data))
  }, [])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Job Board</h1>
      <div className="grid gap-4">
        {jobs.map((j) => (
          <div key={j.id} className="bg-white p-4 rounded shadow">
            <h3 className="font-semibold">{j.job_title}</h3>
            <p className="text-sm text-gray-500">{j.company_name}</p>
            <p className="text-sm text-gray-600 mt-1">{j.description}</p>
            <div className="text-xs text-gray-400 mt-2">Required Tier: {j.required_tier_level}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
