import { apiClient } from './api';
import type { PaginatedMatchesResponse, MatchResponse } from '../types/api';

export const matchingService = {
  getMatches: async (params?: { 
    cpse?: string; 
    classification?: string; 
    status?: string; 
    review_required?: boolean; 
    page?: number; 
    page_size?: number;
  }): Promise<PaginatedMatchesResponse> => {
    // Convert boolean to string for URL params if defined
    const queryParams: Record<string, string> = {};
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams[key] = String(value);
        }
      });
    }
    return apiClient.get<PaginatedMatchesResponse>('/matching', { params: queryParams });
  },
  
  getMatchDetail: async (id: number): Promise<MatchResponse> => {
    return apiClient.get<MatchResponse>(`/matching/${id}`);
  }
};
