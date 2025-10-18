import { useState, useEffect } from 'react'

interface HealthStatus {
  status: string;
  mode?: string;
}

interface LLMEvent {
  id: string;
  time: string;
  model: string;
  provider: string;
  tokens_total: number;
  tokens_prompt: number;
  tokens_completion: number;
  cost_usd: number;
  latency_ms: number;
  has_error: boolean;
  status: string;
  user_id?: string;
  session_id?: string;
}

interface Stats {
  total_events_stored: number;
  queue_length: number;
  dlq_length: number;
}

function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [events, setEvents] = useState<LLMEvent[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)

  const API_KEY = 'llmscope-local-key'

  const fetchData = async () => {
    try {
      // Fetch health
      const healthRes = await fetch('/health')
      const healthData = await healthRes.json()
      setHealth(healthData)

      // Fetch recent events
      const eventsRes = await fetch('/api/v1/events/recent?limit=50', {
        headers: { 'X-API-Key': API_KEY }
      })
      const eventsData = await eventsRes.json()
      setEvents(eventsData.events || [])

      // Fetch stats
      const statsRes = await fetch('/api/v1/events/stats', {
        headers: { 'X-API-Key': API_KEY }
      })
      const statsData = await statsRes.json()
      setStats(statsData)

      setLoading(false)
    } catch (error) {
      console.error('Error fetching data:', error)
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [])

  // Calculate aggregate metrics from events
  const totalTokens = events.reduce((sum, e) => sum + (e.tokens_total || 0), 0)
  const totalCost = events.reduce((sum, e) => sum + (e.cost_usd || 0), 0)
  const avgLatency = events.length > 0
    ? events.reduce((sum, e) => sum + (e.latency_ms || 0), 0) / events.length
    : 0

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 text-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-5xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
            LLMScope Dashboard
          </h1>
          <p className="text-gray-300">Real-time LLM observability and analytics</p>
        </div>

        {/* System Status */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-4 mb-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`h-3 w-3 rounded-full ${health?.status === 'healthy' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
              <span className="font-semibold">System Status:</span>
              <span className={health?.status === 'healthy' ? 'text-green-400' : 'text-red-400'}>
                {health?.status || 'Unknown'}
              </span>
              {health?.mode && (
                <>
                  <span className="text-gray-400">•</span>
                  <span className="text-gray-400">{health.mode} mode</span>
                </>
              )}
            </div>
            <div className="flex items-center gap-4 text-sm text-gray-400">
              <span>Queue: {stats?.queue_length || 0}</span>
              <span>DLQ: {stats?.dlq_length || 0}</span>
              <a href="/docs" target="_blank" className="text-blue-400 hover:text-blue-300">API Docs</a>
            </div>
          </div>
        </div>

        {/* Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/20 rounded-lg p-6 border border-blue-500/30">
            <div className="text-blue-400 text-sm font-semibold mb-2">TOTAL EVENTS</div>
            <div className="text-3xl font-bold">{stats?.total_events_stored?.toLocaleString() || 0}</div>
            <div className="text-gray-400 text-sm mt-1">Stored in database</div>
          </div>

          <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/20 rounded-lg p-6 border border-purple-500/30">
            <div className="text-purple-400 text-sm font-semibold mb-2">TOTAL TOKENS</div>
            <div className="text-3xl font-bold">{totalTokens.toLocaleString()}</div>
            <div className="text-gray-400 text-sm mt-1">Last 50 events</div>
          </div>

          <div className="bg-gradient-to-br from-green-500/20 to-green-600/20 rounded-lg p-6 border border-green-500/30">
            <div className="text-green-400 text-sm font-semibold mb-2">TOTAL COST</div>
            <div className="text-3xl font-bold">${totalCost.toFixed(4)}</div>
            <div className="text-gray-400 text-sm mt-1">Last 50 events</div>
          </div>

          <div className="bg-gradient-to-br from-orange-500/20 to-orange-600/20 rounded-lg p-6 border border-orange-500/30">
            <div className="text-orange-400 text-sm font-semibold mb-2">AVG LATENCY</div>
            <div className="text-3xl font-bold">{avgLatency.toFixed(0)}ms</div>
            <div className="text-gray-400 text-sm mt-1">Last 50 events</div>
          </div>
        </div>

        {/* Recent Events Table */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg border border-gray-700 overflow-hidden">
          <div className="p-4 border-b border-gray-700 flex items-center justify-between">
            <h2 className="text-xl font-semibold">Recent Events</h2>
            <div className="flex items-center gap-2">
              <div className={`h-2 w-2 rounded-full bg-green-500 ${loading ? '' : 'animate-pulse'}`}></div>
              <span className="text-sm text-gray-400">Auto-refresh: 5s</span>
            </div>
          </div>

          <div className="overflow-x-auto">
            {loading && events.length === 0 ? (
              <div className="text-center py-12 text-gray-400">
                <div className="animate-spin h-8 w-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
                Loading events...
              </div>
            ) : events.length === 0 ? (
              <div className="text-center py-12 text-gray-400">
                <p className="text-lg mb-2">No events yet</p>
                <p className="text-sm">Start sending LLM events to see them here</p>
              </div>
            ) : (
              <table className="w-full">
                <thead className="bg-gray-700/50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-300 uppercase">Time</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-300 uppercase">Model</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-300 uppercase">Provider</th>
                    <th className="px-4 py-3 text-right text-xs font-semibold text-gray-300 uppercase">Tokens</th>
                    <th className="px-4 py-3 text-right text-xs font-semibold text-gray-300 uppercase">Cost</th>
                    <th className="px-4 py-3 text-right text-xs font-semibold text-gray-300 uppercase">Latency</th>
                    <th className="px-4 py-3 text-center text-xs font-semibold text-gray-300 uppercase">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700/50">
                  {events.map((event) => (
                    <tr key={event.id} className="hover:bg-gray-700/30 transition-colors">
                      <td className="px-4 py-3 text-sm text-gray-300">
                        {new Date(event.time).toLocaleTimeString()}
                      </td>
                      <td className="px-4 py-3 text-sm font-medium">{event.model || 'N/A'}</td>
                      <td className="px-4 py-3 text-sm text-gray-300">{event.provider || 'N/A'}</td>
                      <td className="px-4 py-3 text-sm text-right">
                        <div className="flex flex-col">
                          <span className="font-medium">{event.tokens_total?.toLocaleString() || 0}</span>
                          <span className="text-xs text-gray-400">
                            {event.tokens_prompt || 0} → {event.tokens_completion || 0}
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-right font-mono">
                        ${(event.cost_usd || 0).toFixed(6)}
                      </td>
                      <td className="px-4 py-3 text-sm text-right">{event.latency_ms || 'N/A'}ms</td>
                      <td className="px-4 py-3 text-center">
                        {event.has_error ? (
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-red-500/20 text-red-400 border border-red-500/30">
                            Error
                          </span>
                        ) : (
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-500/20 text-green-400 border border-green-500/30">
                            OK
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-gray-400 text-sm">
          <p>LLMScope - High-performance observability for LLM applications</p>
          <div className="mt-2 flex items-center justify-center gap-4">
            <a href="/demo" target="_blank" className="text-blue-400 hover:text-blue-300">Interactive Demo</a>
            <span>•</span>
            <a href="/events/table" target="_blank" className="text-blue-400 hover:text-blue-300">Full Events Table</a>
            <span>•</span>
            <a href="/docs" target="_blank" className="text-blue-400 hover:text-blue-300">API Documentation</a>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
