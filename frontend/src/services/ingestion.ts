import { apiClient } from './api';
import type { IngestionUploadResponse, IngestionJobResponse } from '../types/api';

export const ingestionService = {
  uploadFile: async (file: File, cpse?: string): Promise<IngestionUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    if (cpse) {
      formData.append('cpse', cpse);
    }
    
    return await apiClient.post<IngestionUploadResponse>('/api/ingestion/upload', formData);
  },

  getJob: async (jobId: string): Promise<IngestionJobResponse> => {
    return await apiClient.get<IngestionJobResponse>(`/api/ingestion/jobs/${jobId}`);
  }
};
