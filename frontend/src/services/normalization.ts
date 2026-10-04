import { apiClient } from './api';
import type { NormalizeResponse } from '../types/api';

export const normalizationService = {
  normalizeText: async (description: string): Promise<NormalizeResponse> => {
    return await apiClient.post<NormalizeResponse>('/api/v1/normalization/normalize', {
      description,
    });
  },
};
