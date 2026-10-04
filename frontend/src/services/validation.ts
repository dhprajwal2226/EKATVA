import { apiClient } from './api';
import type { ReviewResponse, ReviewDetailResponse, ReviewActionRequest, ReviewStatus, ReviewPriority } from '../types/api';

export const validationService = {
  getReviews: async (status?: ReviewStatus, priority?: ReviewPriority): Promise<ReviewResponse[]> => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (priority) params.append('priority', priority);
    
    return await apiClient.get<ReviewResponse[]>(`/v1/reviews/?${params.toString()}`);
  },

  getReview: async (id: number): Promise<ReviewDetailResponse> => {
    return await apiClient.get<ReviewDetailResponse>(`/v1/reviews/${id}`);
  },

  approveReview: async (id: number, comment?: string): Promise<ReviewDetailResponse> => {
    const payload: ReviewActionRequest = { comment };
    return await apiClient.post<ReviewDetailResponse>(`/v1/reviews/${id}/approve`, payload);
  },

  rejectReview: async (id: number, comment?: string): Promise<ReviewDetailResponse> => {
    const payload: ReviewActionRequest = { comment };
    return await apiClient.post<ReviewDetailResponse>(`/v1/reviews/${id}/reject`, payload);
  },

  escalateReview: async (id: number, comment?: string, resolution?: string): Promise<ReviewDetailResponse> => {
    const payload: ReviewActionRequest = { comment, resolution };
    return await apiClient.post<ReviewDetailResponse>(`/v1/reviews/${id}/escalate`, payload);
  }
};
