export interface HealthResponse {
  status: string;
  database: string;
  version: string;
}

export interface ApiErrorResponse {
  detail: string | Array<{ loc: string[]; msg: string; type: string }>;
}

export interface OverviewAnalyticsResponse {
  national_materials: number;
  active_materials: number;
  cpse_count: number;
  vendor_count: number;
  location_count: number;
  total_inventory: number;
  total_demand: number;
  potential_gap: number;
  shortage_signals: number;
  surplus_signals: number;
  multi_cpse_materials: number;
  pending_reviews: number;
}


export interface CPSEMappingSummary {
  id: number;
  cpse_code: string;
  material_id: number;
  material_code: string;
  original_description: string;
  mapping_type: string;
  created_at: string;
}

export interface CNMCDetailResponse {
  id: number;
  cnmc: string;
  standard_description: string;
  category: string | null;
  canonical_attributes: Record<string, any>;
  identity_hash: string;
  status: string;
  created_at: string;
  updated_at: string;
  mappings: CPSEMappingSummary[];
}

export interface PaginatedCNMCResponse {
  items: CNMCDetailResponse[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface MaterialItemReference {
  id: number;
  cpse: string;
  code: string;
  description: string;
  normalized_description: string | null;
}

export interface MatchScores {
  semantic: number;
  fuzzy: number;
  attribute: number;
  technical: number;
  final: number;
}

export interface ConflictItem {
  id?: number;
  attribute: string;
  source_value?: string;
  target_value?: string;
  severity: string;
  reason: string;
  created_at?: string;
}

export interface MatchExplanation {
  why_matched: string[];
  what_matched: string[];
  what_differed: string[];
  recommendation: string;
  review_required: boolean;
  confidence: number | null;
  technical_conflicts: ConflictItem[];
}

export interface MatchResponse {
  id: string;
  source_material: MaterialItemReference;
  target_material: MaterialItemReference;
  scores: MatchScores;
  classification: string;
  technical_conflicts: ConflictItem[];
  explanation: MatchExplanation;
  status: string;
  review_required: boolean;
  created_at?: string;
}

export interface PaginatedMatchesResponse {
  items: MatchResponse[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export type ReviewStatus = 'PENDING' | 'IN_PROGRESS' | 'RESOLVED' | 'ESCALATED';
export type ReviewDecision = 'APPROVED' | 'REJECTED' | 'ESCALATED';
export type ReviewPriority = 'HIGH' | 'MEDIUM' | 'LOW';

export interface ReviewHistoryResponse {
  id: number;
  review_id: number;
  changed_by_id?: number | null;
  from_status?: string | null;
  to_status: string;
  decision?: string | null;
  comment?: string | null;
  snapshot?: Record<string, any> | null;
  timestamp: string;
}

export interface ReviewResponse {
  id: number;
  match_id: string;
  reviewer_id?: number | null;
  escalated_by_id?: number | null;
  escalated_at?: string | null;
  escalation_reason?: string | null;
  resolved_by_id?: number | null;
  resolved_at?: string | null;
  resolution?: string | null;
  status: string;
  decision?: string | null;
  reviewer_comment?: string | null;
  rejection_reason?: string | null;
  original_ai_classification?: string | null;
  ai_confidence?: number | null;
  ai_recommendation?: string | null;
  has_critical_conflict: boolean;
  critical_conflict_details?: Record<string, any> | null;
  final_classification?: string | null;
  human_override_reason?: string | null;
  source_cpse_id?: string | null;
  target_cpse_id?: string | null;
  source_material_code?: string | null;
  target_material_code?: string | null;
  priority: string;
  national_material_id?: number | null;
  reviewed_at?: string | null;
  claimed_at?: string | null;
  created_at: string;
  updated_at: string;
  version: number;
}

export interface ReviewDetailResponse extends ReviewResponse {
  history: ReviewHistoryResponse[];
}

export interface ReviewActionRequest {
  comment?: string | null;
  resolution?: string | null;
}

export interface IngestionJobError {
  row: number;
  field: string;
  message: string;
}

export interface IngestionJobResponse {
  job_id: string;
  filename: string;
  status: string;
  total_rows: number;
  processed_rows: number;
  accepted_rows: number;
  rejected_rows: number;
  warnings: number;
  errors: IngestionJobError[];
  created_at: string;
  completed_at?: string | null;
}

export interface IngestionUploadResponse {
  message: string;
  job_id: string;
  status: string;
  filename: string;
}


export interface PassportIdentitySchema {
  description: string;
  category: string;
}

export interface PassportCpseMappingSchema {
  cpse: string;
  code: string;
}

export interface PassportSupplySchema {
  inventory: number;
  reserved: number;
  available: number;
  vendor_count: number;
}

export interface PassportDemandSchema {
  current: number;
  forecast: number;
}

export interface PassportIntelligenceSchema {
  potential_gap?: number | null;
  potential_surplus?: number | null;
  signal: string;
}

export interface PassportGraphSummarySchema {
  cpse_count: number;
  vendor_count: number;
  location_count: number;
}

export interface MaterialPassportResponse {
  cnmc: string;
  status: string;
  identity: PassportIdentitySchema;
  technical_attributes: Record<string, any>;
  cpse_mappings: PassportCpseMappingSchema[];
  supply: PassportSupplySchema;
  demand: PassportDemandSchema;
  intelligence: PassportIntelligenceSchema;
  graph_summary: PassportGraphSummarySchema;
}

export interface CopilotRequest {
  query: string;
  cnmc_id?: string | null;
}

export interface CopilotResponse {
  answer: string;
  key_findings: string[];
  sources: string[];
  data_limitation?: string | null;
  intent: string;
}

export interface ExecutiveSummaryResponse {
  national_materials: number;
  active_materials: number;
  multi_cpse_materials: number;
  pending_reviews: number;
  shortage_signals: number;
  surplus_signals: number;
  supplier_count: number;
  location_count: number;
  top_shared_materials: any[];
  top_supply_gap_materials: any[];
  top_surplus_materials: any[];
  top_multi_cpse_materials: any[];
}

export interface MaterialAttributeSchema {
  material_type?: string;
  material?: string;
  grade?: string;
  size?: string;
  diameter?: number;
  length?: number;
  width?: number;
  height?: number;
  thickness?: number;
  pressure?: string;
  schedule?: string;
  form?: string;
  standard?: string;
  application?: string;
  manufacturer?: string;
  confidence_scores: Record<string, number>;
  fingerprint_hash?: string;
}

export interface MaterialDNAResponse {
  material_id: number;
  material_code: string;
  original_description: string;
  normalized_description: string;
  attributes: MaterialAttributeSchema;
  fingerprint_hash: string;
  overall_confidence: number;
}

export interface NormalizeRequest {
  description: string;
}

export interface AbbreviationItem {
  abbr: string;
  expansion: string;
}

export interface DimensionItem {
  original_value: number;
  original_unit: string;
  normalized_value: number;
  normalized_unit: string;
  ambiguous: boolean;
}

export interface NormalizeResponse {
  original_description: string;
  normalized_description: string;
  expanded_abbreviations: AbbreviationItem[];
  dimensions: DimensionItem[];
}
