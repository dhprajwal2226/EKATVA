import { getExecutiveSummary } from './analytics';
import type { ExecutiveSummaryResponse } from '../types/api';

export const getProcurementIntelligence = (): Promise<ExecutiveSummaryResponse> => {
  return getExecutiveSummary();
};
