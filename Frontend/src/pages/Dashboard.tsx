import { useQuery } from '@tanstack/react-query'
import { Database, Network, Search, FileText } from 'lucide-react'
import { nodeApi } from '../services/api'

export default function Dashboard() {
  // This is a placeholder - you'd need to add a stats endpoint to your API
  const stats = {
    nodes: 0,
    edges: 0,
    searches: 0,
    pdfs: 0,
  }

  const statCards = [
    { label: 'Total Nodes', value: stats.nodes, icon: Database, color: 'bg-blue-500' },
    { label: 'Total Edges', value: stats.edges, icon: Network, color: 'bg-green-500' },
    { label: 'Searches', value: stats.searches, icon: Search, color: 'bg-purple-500' },
    { label: 'PDFs Processed', value: stats.pdfs, icon: FileText, color: 'bg-orange-500' },
  ]

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Overview of your hybrid vector + graph database</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.label} className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stat.value}</p>
                </div>
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a
            href="/nodes"
            className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
          >
            <Database className="h-6 w-6 text-primary-600 mb-2" />
            <h3 className="font-medium text-gray-900">Create Node</h3>
            <p className="text-sm text-gray-600 mt-1">Add a new node to the graph</p>
          </a>
          <a
            href="/search"
            className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
          >
            <Search className="h-6 w-6 text-primary-600 mb-2" />
            <h3 className="font-medium text-gray-900">Search</h3>
            <p className="text-sm text-gray-600 mt-1">Perform vector, graph, or hybrid search</p>
          </a>
          <a
            href="/pdf"
            className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
          >
            <FileText className="h-6 w-6 text-primary-600 mb-2" />
            <h3 className="font-medium text-gray-900">Upload PDF</h3>
            <p className="text-sm text-gray-600 mt-1">Process and index a PDF document</p>
          </a>
        </div>
      </div>

      {/* System Info */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">System Architecture</h2>
        <div className="space-y-3 text-sm text-gray-600">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>Vector Database: ChromaDB with HuggingFace embeddings</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span>Graph Database: NetworkX MultiDiGraph</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
            <span>Hybrid Retrieval: Weighted combination of vector + graph scores</span>
          </div>
        </div>
      </div>
    </div>
  )
}

