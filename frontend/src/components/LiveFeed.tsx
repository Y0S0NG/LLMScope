/**
 * Live event feed component
 */
import React, { useEffect, useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

interface Event {
  id: string;
  timestamp: string;
  model: string;
  provider: string;
  total_tokens: number;
  latency_ms: number;
  cost: number;
}

const LiveFeed: React.FC = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const { message, isConnected } = useWebSocket();

  useEffect(() => {
    if (message) {
      setEvents((prev) => [message, ...prev].slice(0, 50)); // Keep last 50 events
    }
  }, [message]);

  return (
    <div className="live-feed">
      <div className="connection-status">
        {isConnected ? (
          <span className="status-connected">● Connected</span>
        ) : (
          <span className="status-disconnected">● Disconnected</span>
        )}
      </div>

      <div className="events-list">
        {events.length === 0 ? (
          <p>Waiting for events...</p>
        ) : (
          events.map((event) => (
            <div key={event.id} className="event-item">
              <span className="event-time">
                {new Date(event.timestamp).toLocaleTimeString()}
              </span>
              <span className="event-model">{event.model}</span>
              <span className="event-tokens">{event.total_tokens} tokens</span>
              <span className="event-latency">{event.latency_ms.toFixed(0)}ms</span>
              <span className="event-cost">${event.cost.toFixed(4)}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default LiveFeed;
