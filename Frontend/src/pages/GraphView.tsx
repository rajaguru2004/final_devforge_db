import { useEffect, useRef, useState } from 'react'
// @ts-ignore - vis-network includes types but they may not be properly exported
import { Network, DataSet } from 'vis-network/standalone'
import { RefreshCw } from 'lucide-react'

export default function GraphView() {
  const containerRef = useRef<HTMLDivElement>(null)
  const networkRef = useRef<any>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (!containerRef.current) return

    // Note: You'd need to add an endpoint to fetch graph data
    // For now, this is a placeholder structure
    const nodes = new DataSet<any>([])
    const edges = new DataSet<any>([])

    const data = { nodes, edges }
    const options = {
      nodes: {
        shape: 'dot',
        size: 20,
        font: {
          size: 14,
        },
        borderWidth: 2,
        color: {
          border: '#2B7CE9',
          background: '#97C2FC',
          highlight: {
            border: '#2B7CE9',
            background: '#D2E5FF',
          },
        },
      },
      edges: {
        width: 2,
        color: {
          color: '#848484',
          highlight: '#848484',
        },
        smooth: {
          type: 'continuous',
        },
      },
      physics: {
        enabled: true,
        stabilization: {
          iterations: 200,
        },
      },
      interaction: {
        hover: true,
        tooltipDelay: 200,
      },
    }

    const network = new Network(containerRef.current, data, options)
    networkRef.current = network

    // Handle node click
    network.on('click', (params) => {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0]
        console.log('Clicked node:', nodeId)
        // You could open a modal or navigate to node details
      }
    })

    setIsLoading(false)

    return () => {
      network.destroy()
    }
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Graph Visualization</h1>
          <p className="text-gray-600 mt-2">Interactive visualization of the knowledge graph</p>
        </div>
        <button
          onClick={() => {
            // Refresh graph data
            setIsLoading(true)
            setTimeout(() => setIsLoading(false), 500)
          }}
          className="btn btn-secondary flex items-center space-x-2"
        >
          <RefreshCw className="h-5 w-5" />
          <span>Refresh</span>
        </button>
      </div>

      <div className="card p-0 overflow-hidden">
        <div
          ref={containerRef}
          className="w-full h-[600px] bg-gray-50"
          style={{ minHeight: '600px' }}
        />
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading graph...</p>
            </div>
          </div>
        )}
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-2">Instructions</h2>
        <ul className="text-sm text-gray-600 space-y-1 list-disc list-inside">
          <li>Drag nodes to rearrange the graph</li>
          <li>Click on nodes to view details</li>
          <li>Zoom with mouse wheel or pinch gesture</li>
          <li>Pan by dragging the background</li>
        </ul>
        <p className="text-xs text-gray-500 mt-4">
          Note: Add a GET /graph endpoint to your API to fetch graph data for visualization
        </p>
      </div>
    </div>
  )
}

