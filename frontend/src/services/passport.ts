import { apiClient } from './api';
import type { MaterialPassportResponse } from '../types/api';

export const passportService = {
  getPassport: async (cnmc: string): Promise<MaterialPassportResponse> => {
    return await apiClient.get<MaterialPassportResponse>(`/api/v1/passport/${cnmc}`);
  }
};
