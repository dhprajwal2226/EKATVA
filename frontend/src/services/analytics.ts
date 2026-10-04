import { apiClient } from './api';
import type { OverviewAnalyticsResponse, ExecutiveSummaryResponse } from '../types/api';

export const getOverview = (): Promise<OverviewAnalyticsResponse> => {
  return apiClient.get<OverviewAnalyticsResponse>('/api/v1/analytics/overview');
};

export const getExecutiveSummary = (): Promise<ExecutiveSummaryResponse> => {
  return apiClient.get<ExecutiveSummaryResponse>('/api/v1/analytics/executive-summary');
};

export const getCategories = (): Promise<any> => {
  return apiClient.get<any>('/api/v1/analytics/categories');
};

export const getTrends = (): Promise<any> => {
  return apiClient.get<any>('/api/v1/analytics/trends');
};

export const getMatching = (): Promise<any> => {
  return apiClient.get<any>('/api/v1/analytics/matching');
};
