import { apiClient } from './api';
import type { CopilotRequest, CopilotResponse } from '../types/api';

export const copilotService = {
  query: (data: CopilotRequest) => 
    apiClient.post<CopilotResponse>('/api/v1/copilot/query', data),
};
