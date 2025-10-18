import { Link } from 'react-router-dom';

export const Landing = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Hero Section */}
      <div className="container mx-auto px-4 pt-20 pb-32">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-6xl font-bold text-gray-900 mb-6">
            LLMScope Playground
          </h1>
          <p className="text-2xl text-gray-600 mb-8">
            Monitor and analyze your LLM API calls in real-time
          </p>
          <p className="text-lg text-gray-500 mb-12 max-w-2xl mx-auto">
            A session-based monitoring platform for tracking tokens, costs, latency,
            and performance metrics of your LLM interactions.
          </p>

          <Link
            to="/playground"
            className="inline-block px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-lg font-semibold rounded-lg shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all"
          >
            Try Playground →
          </Link>
        </div>
      </div>

      {/* Features Section */}
      <div className="container mx-auto px-4 pb-20">
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <div className="bg-white p-8 rounded-xl shadow-md">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-xl font-bold mb-3">Real-time Metrics</h3>
            <p className="text-gray-600">
              Track tokens, costs, and latency for every LLM API call in real-time.
            </p>
          </div>

          <div className="bg-white p-8 rounded-xl shadow-md">
            <div className="text-4xl mb-4">🔒</div>
            <h3 className="text-xl font-bold mb-3">Session-Based</h3>
            <p className="text-gray-600">
              No account required. Each visitor gets an isolated session automatically.
            </p>
          </div>

          <div className="bg-white p-8 rounded-xl shadow-md">
            <div className="text-4xl mb-4">⚡</div>
            <h3 className="text-xl font-bold mb-3">Fast & Simple</h3>
            <p className="text-gray-600">
              Start monitoring immediately. No complex setup or configuration needed.
            </p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-gray-200 bg-white">
        <div className="container mx-auto px-4 py-8 text-center text-gray-600">
          <p>Built with React, FastAPI, and PostgreSQL</p>
        </div>
      </div>
    </div>
  );
};
