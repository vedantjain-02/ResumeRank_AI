/* ------------------------------------------------------------------
 * TypeScript mirrors of the FastAPI schemas (app/schemas/*.py).
 * Keep these in sync with the backend contract — do not guess fields.
 * ------------------------------------------------------------------ */

// ---------- Job ----------

export interface Job {
  id: number;
  title: string;
  description: string;
  required_skills: string | null;
  preferred_skills: string | null;
  minimum_experience: number | null;
  education_requirement: string | null;
  responsibilities: string | null;
  certifications_required: string | null;
  is_mandatory_requirements: string | null;
  created_at?: string | null;
}

export interface JobListResponse {
  total: number;
  jobs: Job[];
}

// ---------- Candidate ----------

export interface FunctionalExpertiseItem {
  area: string;
  details?: string | null;
  years?: number | null;
}

export interface LeadershipDetails {
  has_leadership: boolean;
  roles: string[];
  team_size: number | null;
  responsibilities: string[];
}

export interface EducationItem {
  degree?: string | null;
  field?: string | null;
  institution?: string | null;
  graduation_year?: number | null;
}

export interface Candidate {
  id: number;
  name: string | null;
  phone_number: string | null;
  career_summary: string | null;
  total_experience_years: number | null;
  seniority_level: string | null;
  job_title: string | null;
  functional_expertise: FunctionalExpertiseItem[];
  leadership: LeadershipDetails;
  education: EducationItem[];
  capability_tags: string[];
  is_seed: boolean;
  created_at?: string | null;
}

export interface CandidateDetail extends Candidate {
  resume_text: string | null;
}

export interface CandidateListResponse {
  total: number;
  candidates: Candidate[];
}

export interface CandidateUploadResponse {
  id: number;
  name: string | null;
  message: string;
  career_summary_preview: string;
}

// ---------- Ranking ----------

export interface RankingRequest {
  top_n: number;
}

/**
 * Score breakdown as returned inside `score_breakdown` on a ranking result.
 * These names come straight from ranking_service.compute_final_score breakdown dict.
 */
export interface ScoreBreakdown {
  hard_filter_result?: string;
  pool_level?: number;
  bm25_score?: number | null;
  vector_similarity_score?: number | null;
  hybrid_retrieval_score?: number | null;
  skills_score?: number | null;
  experience_score?: number | null;
  semantic_score?: number | null;
  education_score?: number | null;
  final_score?: number | null;
  mandatory_skills_satisfied?: boolean;
  missing_mandatory?: string[];
}

export interface RankingCandidateResult {
  rank: number;
  candidate_id: number;
  candidate_name: string;
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  experience_match: string;
  explanation: string;
  career_summary?: string | null;
  score_breakdown?: ScoreBreakdown | null;
  resume_id: number;
  skills_score?: number | null;
  experience_score?: number | null;
  semantic_score?: number | null;
  education_score?: number | null;
}

export interface HardFilterAttempt {
  level: string;
  pool_size: number;
  mandatory_skills?: number;
  additions?: number;
}

export interface PipelineStats {
  total_candidates_evaluated: number;
  selected_limit: number;
  strict_hard_filtered: number;
  relaxed_candidates: number;
  hard_filtered: number;
  hard_filter_trimmed: number;
  bm25_retrieved: number;
  vector_retrieved: number;
  fused_pool: number;
  final_ranked: number;
  bm25_weight: number;
  vector_weight: number;
  hard_filter_limit: number;
  parsed_mandatory_skills: string[];
  parsed_preferred_skills: string[];
  parsed_inferred_skills: string[];
  maximum_experience: number | null;
  hard_filter_attempts: HardFilterAttempt[];
  hard_filter_conditions: string[];
  relaxation_reason: string | null;
  configuration?: Record<string, unknown>;
  final_hybrid_weight?: number;
  final_detailed_weight?: number;
  enable_final_hybrid?: boolean;
  enable_mandatory_priority?: boolean;
}

export interface RankingResponse {
  job_id: number;
  job_title: string;
  total_candidates_evaluated: number;
  top_candidates: RankingCandidateResult[];
  pipeline_stats?: PipelineStats | null;
}

export interface RankingResultsResponse {
  job_id: number;
  job_title: string;
  total_results: number;
  results: RankingCandidateResult[];
}

export type RelaxationLevel = "strict" | "relaxed_mandatory" | "relaxed_all" | "baseline" | "none";

export function relaxationMode(stats?: PipelineStats | null): {
  mode: RelaxationLevel;
  label: string;
  reason: string | null;
} {
  if (!stats) return { mode: "none", label: "N/A", reason: null };
  const attempts: HardFilterAttempt[] = stats.hard_filter_attempts ?? [];
  if (attempts.length <= 1) return { mode: "strict", label: "Strict", reason: stats.relaxation_reason };
  const used = attempts[attempts.length - 1];
  const mode = (used?.level ?? "strict") as RelaxationLevel;
  const labels: Record<string, string> = {
    strict: "Strict",
    relaxed_mandatory: "Relaxed Mandatory",
    relaxed_all: "Relaxed All",
    baseline: "Baseline",
  };
  return { mode, label: labels[mode] ?? mode, reason: stats.relaxation_reason };
}

// ---------- Health / weights ----------

export interface HealthResponse {
  status: string;
  version: string;
}

export interface WeightsResponse {
  scoring_weights: Record<string, number>;
}

export interface ApiErrorPayload {
  detail?: string;
  [key: string]: unknown;
}