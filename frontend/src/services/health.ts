import { apiClient } from './api';
import type { HealthResponse } from '../types/api';

export const getHealth = (): Promise<HealthResponse> => {
  return apiClient.get<HealthResponse>('/health');
};
