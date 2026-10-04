import { apiClient } from './api';
import type { MaterialDNAResponse } from '../types/api';

export const dnaService = {
  getMaterialDNA: async (materialId: number): Promise<MaterialDNAResponse> => {
    return await apiClient.get<MaterialDNAResponse>(`/api/v1/materials/${materialId}/dna`);
  },
};
