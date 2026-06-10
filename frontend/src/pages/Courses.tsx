import { useEffect, useState } from 'react'
import api from '@/api/client'

interface Course {
  id: number
  title: string
  short_summary: string
  total_estimated_hours: number
  difficulty_level: string
}

export default function Courses() {
  const [courses, setCourses] = useState<Course[]>([])

  useEffect(() => {
    api.get('/courses/').then((res) => setCourses(res.data))
  }, [])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Courses</h1>
      <div className="grid gap-4">
        {courses.map((c) => (
          <div key={c.id} className="bg-white p-4 rounded shadow">
            <h3 className="font-semibold">{c.title}</h3>
            <p className="text-sm text-gray-600">{c.short_summary}</p>
            <div className="text-xs text-gray-400 mt-2">
              {c.difficulty_level} | {c.total_estimated_hours} hours
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
