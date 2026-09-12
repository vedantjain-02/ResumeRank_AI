import {
  CandidateDetail,
  CandidateListResponse,
  CandidateUploadResponse,
  HealthResponse,
  Job,
  JobListResponse,
  RankingResponse,
  RankingResultsResponse,
  WeightsResponse,
} from "@/lib/types";

/**
 * Central API client for the FastAPI backend.
 *
 * Base URL is configured via NEXT_PUBLIC_API_BASE_URL (see .env.example).
 * Defaults to the local backend for development.
 */
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/+$/, "") || "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;
  payload: unknown;

  constructor(message: string, status: number, payload: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

export function isApiError(err: unknown): err is ApiError {
  return err instanceof ApiError;
}

function extractDetail(payload: unknown): string {
  if (payload && typeof payload === "object") {
    const p = payload as Record<string, unknown>;
    if (typeof p.detail === "string") return p.detail;
    if (Array.isArray(p.detail)) {
      return p.detail
        .map((d) => {
          if (d && typeof d === "object") {
            const dd = d as Record<string, unknown>;
            return dd.msg ? String(dd.msg) : JSON.stringify(d);
          }
          return String(d);
        })
        .join("; ");
    }
  }
  return "Request failed";
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: init?.body instanceof FormData ? undefined : { "Content-Type": "application/json", ...init?.headers },
    });
  } catch (err) {
    const reason = err instanceof Error ? err.message : "Unknown network error";
    throw new ApiError(
      `Could not reach the backend at ${API_BASE_URL}. Is the FastAPI server running? (${reason})`,
      0,
      err,
    );
  }

  if (!res.ok) {
    let payload: unknown = null;
    try {
      payload = await res.json();
    } catch {
      payload = await res.text().catch(() => null);
    }
    throw new ApiError(extractDetail(payload) || `HTTP ${res.status}`, res.status, payload);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

// ---------- Health ----------

export async function fetchHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/api/health");
}

// ---------- Weights ----------

export async function fetchWeights(): Promise<WeightsResponse> {
  return request<WeightsResponse>("/api/weights");
}

// ---------- Jobs ----------

export async function fetchJobs(): Promise<JobListResponse> {
  return request<JobListResponse>("/api/jobs");
}

export interface CreateJobInput {
  title?: string;
  description?: string;
  file?: File | null;
}

export async function createJob(input: CreateJobInput): Promise<Job> {
  const form = new FormData();
  if (input.title?.trim()) form.append("title", input.title.trim());
  if (input.file) {
    form.append("file", input.file);
  } else if (input.description?.trim()) {
    form.append("description", input.description);
  } else {
    throw new ApiError("Add a job description text or upload a JD file.", 0, null);
  }
  return request<Job>("/api/jobs", { method: "POST", body: form });
}

// ---------- Ranking ----------

export async function rankJob(jobId: number, topN: number): Promise<RankingResponse> {
  return request<RankingResponse>(
    `/api/jobs/${jobId}/rank?top_n=${encodeURIComponent(topN)}`,
    { method: "POST" },
  );
}

export async function fetchRankingResults(jobId: number, limit = 10): Promise<RankingResultsResponse> {
  return request<RankingResultsResponse>(`/api/jobs/${jobId}/results?limit=${encodeURIComponent(limit)}`);
}

// ---------- Candidates ----------

export interface FetchCandidatesParams {
  search?: string;
  seniority_level?: string;
  skill?: string;
  min_experience?: number;
  max_experience?: number;
  limit?: number;
  offset?: number;
}

export async function fetchCandidates(params: FetchCandidatesParams = {}): Promise<CandidateListResponse> {
  const qs = new URLSearchParams();
  if (params.search) qs.set("search", params.search);
  if (params.seniority_level) qs.set("seniority_level", params.seniority_level);
  if (params.skill) qs.set("skill", params.skill);
  if (params.min_experience != null) qs.set("min_experience", String(params.min_experience));
  if (params.max_experience != null) qs.set("max_experience", String(params.max_experience));
  qs.set("limit", String(params.limit ?? 12));
  qs.set("offset", String(params.offset ?? 0));
  const q = qs.toString();
  return request<CandidateListResponse>(`/api/candidates${q ? `?${q}` : ""}`);
}

export async function fetchCandidate(id: number): Promise<CandidateDetail> {
  return request<CandidateDetail>(`/api/candidates/${id}`);
}

export async function uploadResume(file: File): Promise<CandidateUploadResponse> {
  const form = new FormData();
  form.append("file", file);
  return request<CandidateUploadResponse>("/api/candidates/upload", { method: "POST", body: form });
}