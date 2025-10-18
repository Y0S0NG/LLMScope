import { useSession } from '../contexts/SessionContext';
import { useEffect } from 'react';

export const MetricsPanel = () => {
  const { metrics, sessionInfo, refreshMetrics, isLoading } = useSession();

  // Auto-refresh metrics every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      refreshMetrics();
    }, 5000);

    return () => clearInterval(interval);
  }, [refreshMetrics]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-gray-500">Loading metrics...</div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto p-6 space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-800 mb-1">Session Metrics</h2>
        <p className="text-sm text-gray-500">Live updates every 5 seconds</p>
      </div>

      {/* Metrics Cards */}
      <div className="space-y-4">
        {/* Total Events */}
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-lg border border-blue-200">
          <div className="text-sm text-blue-600 font-semibold mb-1">Total Events</div>
          <div className="text-4xl font-bold text-blue-900">
            {metrics?.event_count || 0}
          </div>
        </div>

        {/* Total Tokens */}
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-lg border border-purple-200">
          <div className="text-sm text-purple-600 font-semibold mb-1">Total Tokens</div>
          <div className="text-4xl font-bold text-purple-900">
            {(metrics?.total_tokens || 0).toLocaleString()}
          </div>
        </div>

        {/* Total Cost */}
        <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-lg border border-green-200">
          <div className="text-sm text-green-600 font-semibold mb-1">Total Cost</div>
          <div className="text-4xl font-bold text-green-900">
            ${(metrics?.total_cost || 0).toFixed(4)}
          </div>
        </div>

        {/* Models Used */}
        {metrics && metrics.models_used.length > 0 && (
          <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
            <div className="text-sm text-gray-600 font-semibold mb-3">Models Used</div>
            <div className="space-y-2">
              {metrics.models_used.map((model, idx) => (
                <div key={idx} className="text-sm text-gray-700 font-mono bg-white px-3 py-2 rounded">
                  {model}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Session Info */}
        {sessionInfo && (
          <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
            <div className="text-sm text-gray-600 font-semibold mb-3">Session Info</div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Created:</span>
                <span className="text-gray-700">
                  {new Date(sessionInfo.created_at).toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Last Active:</span>
                <span className="text-gray-700">
                  {new Date(sessionInfo.last_activity).toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Status:</span>
                <span className={`font-semibold ${sessionInfo.is_active ? 'text-green-600' : 'text-red-600'}`}>
                  {sessionInfo.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
