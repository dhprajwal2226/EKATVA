import { apiClient } from './api';
import type { PaginatedCNMCResponse, CNMCDetailResponse } from '../types/api';

export const cnmcService = {
  getCNMCs: async (params?: { category?: string; status?: string; page?: number; page_size?: number }): Promise<PaginatedCNMCResponse> => {
    return apiClient.get<PaginatedCNMCResponse>('/api/cnmc', { params: params as Record<string, string> });
  },
  
  getCNMCDetail: async (id: number): Promise<CNMCDetailResponse> => {
    return apiClient.get<CNMCDetailResponse>(`/api/cnmc/${id}`);
  }
};
