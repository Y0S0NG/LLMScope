import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import {
  createSession,
  getCurrentSessionInfo,
  getCurrentSessionMetrics,
  resetCurrentSession,
  setSessionId as setApiSessionId,
} from '../api/client';
import type { SessionInfo, SessionMetrics, StoredSession } from '../types';

interface SessionContextType {
  sessionId: string | null;
  sessionInfo: SessionInfo | null;
  metrics: SessionMetrics | null;
  isLoading: boolean;
  error: string | null;
  createNewSession: () => Promise<void>;
  resetSession: () => Promise<void>;
  refreshMetrics: () => Promise<void>;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

const STORAGE_KEY = 'llmscope_session';

export const SessionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionInfo, setSessionInfo] = useState<SessionInfo | null>(null);
  const [metrics, setMetrics] = useState<SessionMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load session from localStorage
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const data: StoredSession = JSON.parse(stored);
        setSessionId(data.sessionId);
        setApiSessionId(data.sessionId);
      } catch (err) {
        console.error('Failed to parse stored session:', err);
        localStorage.removeItem(STORAGE_KEY);
      }
    }
  }, []);

  // Save session to localStorage
  const saveSession = useCallback((id: string) => {
    const data: StoredSession = {
      sessionId: id,
      createdAt: new Date().toISOString(),
      lastActivity: new Date().toISOString(),
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    setSessionId(id);
    setApiSessionId(id);
  }, []);

  // Create new session
  const createNewSession = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await createSession();
      saveSession(response.session_id);
      // Fetch session info after creating
      await fetchSessionInfo(response.session_id);
      await fetchMetrics(response.session_id);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create session';
      setError(message);
      console.error('Error creating session:', err);
    } finally {
      setIsLoading(false);
    }
  }, [saveSession]);

  // Fetch session info
  const fetchSessionInfo = useCallback(async (id?: string) => {
    const currentId = id || sessionId;
    if (!currentId) return;

    try {
      setApiSessionId(currentId);
      const info = await getCurrentSessionInfo();
      setSessionInfo(info);
    } catch (err) {
      console.error('Error fetching session info:', err);
      // If session not found, create a new one
      if (axios.isAxiosError(err) && err.response?.status === 404) {
        await createNewSession();
      }
    }
  }, [sessionId, createNewSession]);

  // Fetch metrics
  const fetchMetrics = useCallback(async (id?: string) => {
    const currentId = id || sessionId;
    if (!currentId) return;

    try {
      setApiSessionId(currentId);
      const metricsData = await getCurrentSessionMetrics();
      setMetrics(metricsData);
    } catch (err) {
      console.error('Error fetching metrics:', err);
    }
  }, [sessionId]);

  // Refresh metrics
  const refreshMetrics = useCallback(async () => {
    await fetchMetrics();
  }, [fetchMetrics]);

  // Reset session
  const resetSession = useCallback(async () => {
    if (!sessionId) return;

    try {
      setIsLoading(true);
      setError(null);
      await resetCurrentSession();
      // Refresh data after reset
      await fetchSessionInfo();
      await fetchMetrics();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to reset session';
      setError(message);
      console.error('Error resetting session:', err);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, fetchSessionInfo, fetchMetrics]);

  // Initialize session on mount
  useEffect(() => {
    const initSession = async () => {
      if (sessionId) {
        // Try to fetch existing session
        await fetchSessionInfo();
        await fetchMetrics();
        setIsLoading(false);
      } else {
        // Create new session if none exists
        await createNewSession();
      }
    };

    initSession();
  }, []); // Only run once on mount

  const value: SessionContextType = {
    sessionId,
    sessionInfo,
    metrics,
    isLoading,
    error,
    createNewSession,
    resetSession,
    refreshMetrics,
  };

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
};

export const useSession = () => {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
};

// Fix axios import
import axios from 'axios';
