/**
 * Analytics hook
 */
import { apiClient } from '../api/client';

export const useAnalytics = () => {
  const getMetrics = async (params?: {
    startTime?: string;
    endTime?: string;
    model?: string;
  }) => {
    const queryParams = new URLSearchParams();
    if (params?.startTime) queryParams.append('start_time', params.startTime);
    if (params?.endTime) queryParams.append('end_time', params.endTime);
    if (params?.model) queryParams.append('model', params.model);

    const url = `/analytics/metrics${queryParams.toString() ? '?' + queryParams : ''}`;
    return await apiClient.get(url);
  };

  const getCostBreakdown = async (params?: {
    startTime?: string;
    endTime?: string;
  }) => {
    const queryParams = new URLSearchParams();
    if (params?.startTime) queryParams.append('start_time', params.startTime);
    if (params?.endTime) queryParams.append('end_time', params.endTime);

    const url = `/analytics/costs${queryParams.toString() ? '?' + queryParams : ''}`;
    const data = await apiClient.get(url);
    return data.breakdown;
  };

  return { getMetrics, getCostBreakdown };
};
