import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Trash2, Edit, Search } from 'lucide-react'
import { nodeApi, type Node, type NodeCreate, type NodeUpdate } from '../services/api'

export default function Nodes() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingNode, setEditingNode] = useState<Node | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const queryClient = useQueryClient()

  // Note: You'd need to add a list endpoint to your API
  // For now, this is a placeholder structure

  const createMutation = useMutation({
    mutationFn: (data: NodeCreate) => nodeApi.create(data).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['nodes'] })
      setShowCreateModal(false)
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: NodeUpdate }) =>
      nodeApi.update(id, data).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['nodes'] })
      setEditingNode(null)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => nodeApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['nodes'] })
    },
  })

  const handleCreate = (data: NodeCreate) => {
    createMutation.mutate(data)
  }

  const handleUpdate = (id: string, data: NodeUpdate) => {
    updateMutation.mutate({ id, data })
  }

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this node?')) {
      deleteMutation.mutate(id)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Nodes</h1>
          <p className="text-gray-600 mt-2">Manage graph nodes and their content</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn btn-primary flex items-center space-x-2"
        >
          <Plus className="h-5 w-5" />
          <span>Create Node</span>
        </button>
      </div>

      {/* Search Bar */}
      <div className="card">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search nodes by text or metadata..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input pl-10"
          />
        </div>
      </div>

      {/* Nodes List */}
      <div className="card">
        <p className="text-gray-500 text-center py-8">
          Node list will appear here. Add a GET /nodes endpoint to your API to fetch all nodes.
        </p>
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <NodeModal
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreate}
          isLoading={createMutation.isPending}
        />
      )}

      {/* Edit Modal */}
      {editingNode && (
        <NodeModal
          node={editingNode}
          onClose={() => setEditingNode(null)}
          onSubmit={(data) => handleUpdate(editingNode.id, data)}
          isLoading={updateMutation.isPending}
        />
      )}
    </div>
  )
}

interface NodeModalProps {
  node?: Node
  onClose: () => void
  onSubmit: (data: NodeCreate | NodeUpdate) => void
  isLoading: boolean
}

function NodeModal({ node, onClose, onSubmit, isLoading }: NodeModalProps) {
  const [text, setText] = useState(node?.text || '')
  const [metadata, setMetadata] = useState(JSON.stringify(node?.metadata || {}, null, 2))
  const [autoEmbed, setAutoEmbed] = useState(true)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const metadataObj = JSON.parse(metadata)
      if (node) {
        onSubmit({ text, metadata: metadataObj, regenerate_embedding: autoEmbed })
      } else {
        onSubmit({ text, metadata: metadataObj, auto_embed: autoEmbed })
      }
    } catch (error) {
      alert('Invalid JSON in metadata field')
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          {node ? 'Edit Node' : 'Create Node'}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Text Content
            </label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              className="input min-h-[100px]"
              required
              placeholder="Enter node text content..."
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Metadata (JSON)
            </label>
            <textarea
              value={metadata}
              onChange={(e) => setMetadata(e.target.value)}
              className="input font-mono text-sm min-h-[150px]"
              placeholder='{"source": "doc1", "category": "example"}'
            />
          </div>
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="autoEmbed"
              checked={autoEmbed}
              onChange={(e) => setAutoEmbed(e.target.checked)}
              className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
            />
            <label htmlFor="autoEmbed" className="text-sm text-gray-700">
              {node ? 'Regenerate embedding' : 'Auto-generate embedding'}
            </label>
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
              {isLoading ? 'Saving...' : node ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

