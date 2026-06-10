export default function Home() {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">Welcome to Kaggle Platform</h1>
      <p className="text-gray-600">
        A data science community for competitions, datasets, notebooks, courses, and jobs.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <Card title="Competitions" desc="Join data science contests and climb the leaderboard." />
        <Card title="Datasets" desc="Explore and share datasets with the community." />
        <Card title="Notebooks" desc="Build and run interactive Jupyter notebooks." />
      </div>
    </div>
  )
}

function Card({ title, desc }: { title: string; desc: string }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition">
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-gray-600 text-sm">{desc}</p>
    </div>
  )
}
