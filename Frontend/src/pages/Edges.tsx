import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import { edgeApi, type EdgeCreate } from '../services/api'

export default function Edges() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const queryClient = useQueryClient()

  const createMutation = useMutation({
    mutationFn: (data: EdgeCreate) => edgeApi.create(data).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['edges'] })
      setShowCreateModal(false)
    },
  })

  const handleCreate = (data: EdgeCreate) => {
    createMutation.mutate(data)
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Edges</h1>
          <p className="text-gray-600 mt-2">Manage relationships between nodes</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn btn-primary flex items-center space-x-2"
        >
          <Plus className="h-5 w-5" />
          <span>Create Edge</span>
        </button>
      </div>

      {/* Edges List */}
      <div className="card">
        <p className="text-gray-500 text-center py-8">
          Edge list will appear here. Add a GET /edges endpoint to your API to fetch all edges.
        </p>
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <EdgeModal
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreate}
          isLoading={createMutation.isPending}
        />
      )}
    </div>
  )
}

interface EdgeModalProps {
  onClose: () => void
  onSubmit: (data: EdgeCreate) => void
  isLoading: boolean
}

function EdgeModal({ onClose, onSubmit, isLoading }: EdgeModalProps) {
  const [source, setSource] = useState('')
  const [target, setTarget] = useState('')
  const [type, setType] = useState('related_to')
  const [weight, setWeight] = useState(1.0)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({ source, target, type, weight })
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Create Edge</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Source Node ID
            </label>
            <input
              type="text"
              value={source}
              onChange={(e) => setSource(e.target.value)}
              className="input"
              required
              placeholder="Enter source node ID"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Target Node ID
            </label>
            <input
              type="text"
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              className="input"
              required
              placeholder="Enter target node ID"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Relationship Type
            </label>
            <input
              type="text"
              value={type}
              onChange={(e) => setType(e.target.value)}
              className="input"
              required
              placeholder="e.g., related_to, contains, references"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Weight: {weight.toFixed(2)}
            </label>
            <input
              type="range"
              value={weight}
              onChange={(e) => setWeight(parseFloat(e.target.value))}
              min="0"
              max="2"
              step="0.1"
              className="w-full"
            />
          </div>
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={isLoading}>
              {isLoading ? 'Creating...' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

