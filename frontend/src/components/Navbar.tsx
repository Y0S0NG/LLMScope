import { Link } from 'react-router-dom';
import { useSession } from '../contexts/SessionContext';

export const Navbar = () => {
  const { sessionId, sessionInfo, resetSession } = useSession();

  return (
    <nav className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-8">
            <Link to="/" className="text-2xl font-bold hover:text-indigo-200 transition">
              LLMScope Playground
            </Link>
            <Link to="/playground" className="hover:text-indigo-200 transition">
              Playground
            </Link>
          </div>

          {sessionId && (
            <div className="flex items-center space-x-4">
              <div className="text-sm">
                <span className="opacity-75">Session:</span>{' '}
                <span className="font-mono">{sessionId.slice(0, 8)}...</span>
              </div>
              {sessionInfo && (
                <div className="text-sm">
                  <span className="opacity-75">Events:</span>{' '}
                  <span className="font-semibold">{sessionInfo.event_count}</span>
                </div>
              )}
              <button
                onClick={resetSession}
                className="px-3 py-1 bg-white/20 hover:bg-white/30 rounded transition text-sm"
              >
                Reset
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};
