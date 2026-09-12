"use client";

import * as React from "react";
import { toast } from "sonner";
import * as api from "@/lib/api";
import type { Job, RankingResponse } from "@/lib/types";
import { API_BASE_URL } from "@/lib/api";

export type BackendStatus = "checking" | "online" | "offline";

export interface RankingActivity {
  jobId: number;
  jobTitle: string;
  topCandidate: string;
  topScore: number;
  candidateCount: number;
  timestamp: number;
}

const LS_ACTIVITY = "rr7-ranking-activity";
const LS_LAST_JOB = "rr7-last-job";
const LS_LAST_TOPN = "rr7-last-topn";
const MAX_ACTIVITY = 10;

function readActivity(): RankingActivity[] {
  try {
    const raw = localStorage.getItem(LS_ACTIVITY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeActivity(list: RankingActivity[]) {
  try {
    localStorage.setItem(LS_ACTIVITY, JSON.stringify(list.slice(0, MAX_ACTIVITY)));
  } catch {
    /* ignore */
  }
}

interface AppContextValue {
  backendStatus: BackendStatus;
  backendVersion: string | null;
  apiBaseUrl: string;
  jobs: Job[];
  jobsLoading: boolean;
  selectedJobId: number | null;
  setSelectedJobId: (id: number | null) => void;
  selectedJob: Job | null;
  candidatesTotal: number;
  ranking: RankingResponse | null;
  rankingLoading: boolean;
  rankingError: string | null;
  activity: RankingActivity[];
  refreshHealth: () => Promise<void>;
  refreshJobs: (preselectId?: number | null) => Promise<Job[]>;
  refreshCandidatesTotal: () => Promise<void>;
  refreshAll: () => Promise<void>;
  runRanking: (jobId: number, topN: number) => Promise<RankingResponse | null>;
  scrollToSection: (id: string) => void;
  activeSection: string;
  setActiveSection: (id: string) => void;
}

const AppContext = React.createContext<AppContextValue | null>(null);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [backendStatus, setBackendStatus] = React.useState<BackendStatus>("checking");
  const [backendVersion, setBackendVersion] = React.useState<string | null>(null);
  const [jobs, setJobs] = React.useState<Job[]>([]);
  const [jobsLoading, setJobsLoading] = React.useState(false);
  const [selectedJobId, setSelectedJobIdState] = React.useState<number | null>(null);
  const [candidatesTotal, setCandidatesTotal] = React.useState(0);
  const [ranking, setRanking] = React.useState<RankingResponse | null>(null);
  const [rankingLoading, setRankingLoading] = React.useState(false);
  const [rankingError, setRankingError] = React.useState<string | null>(null);
  const [activity, setActivity] = React.useState<RankingActivity[]>([]);
  const [activeSection, setActiveSection] = React.useState("dashboard");

  React.useEffect(() => {
    setActivity(readActivity());
    try {
      const last = localStorage.getItem(LS_LAST_JOB);
      if (last) setSelectedJobIdState(parseInt(last, 10) || null);
    } catch {
      /* ignore */
    }
  }, []);

  const refreshHealth = React.useCallback(async () => {
    setBackendStatus("checking");
    try {
      const h = await api.fetchHealth();
      setBackendStatus("online");
      setBackendVersion(h.version);
    } catch {
      setBackendStatus("offline");
      setBackendVersion(null);
    }
  }, []);

  const refreshCandidatesTotal = React.useCallback(async () => {
    try {
      const res = await api.fetchCandidates({ limit: 1, offset: 0 });
      setCandidatesTotal(res.total);
    } catch {
      /* dashboard keeps last known value */
    }
  }, []);

  const refreshJobs = React.useCallback(
    async (preselectId?: number | null) => {
      setJobsLoading(true);
      try {
        const res = await api.fetchJobs();
        setJobs(res.jobs);
        if (preselectId !== undefined) {
          setSelectedJobIdState(
            res.jobs.some((j) => j.id === preselectId) ? preselectId : (res.jobs[0]?.id ?? null),
          );
        } else {
          setSelectedJobIdState((current) =>
            current != null && res.jobs.some((j) => j.id === current) ? current : (res.jobs[0]?.id ?? null),
          );
        }
        return res.jobs;
      } finally {
        setJobsLoading(false);
      }
    },
    [],
  );

  const refreshAll = React.useCallback(async () => {
    await Promise.allSettled([refreshHealth(), refreshJobs(), refreshCandidatesTotal()]);
  }, [refreshHealth, refreshJobs, refreshCandidatesTotal]);

  React.useEffect(() => {
    void refreshAll();
  }, [refreshAll]);

  const setSelectedJobId = React.useCallback(
    (id: number | null) => {
      setSelectedJobIdState(id);
      try {
        if (id == null) localStorage.removeItem(LS_LAST_JOB);
        else localStorage.setItem(LS_LAST_JOB, String(id));
      } catch {
        /* ignore */
      }
    },
    [],
  );

  const runRanking = React.useCallback(
    async (jobId: number, topN: number): Promise<RankingResponse | null> => {
      setRankingLoading(true);
      setRankingError(null);
      try {
        const res = await api.rankJob(jobId, topN);
        setRanking(res);
        setSelectedJobId(jobId);
        const top = res.top_candidates?.[0];
        const entry: RankingActivity = {
          jobId,
          jobTitle: res.job_title,
          topCandidate: top?.candidate_name ?? "—",
          topScore: top?.match_score ?? 0,
          candidateCount: res.total_candidates_evaluated ?? 0,
          timestamp: Date.now(),
        };
        setActivity((prev) => {
          const next = [entry, ...prev.filter((a) => a.jobId !== jobId)].slice(0, MAX_ACTIVITY);
          writeActivity(next);
          return next;
        });
        return res;
      } catch (err) {
        const msg = api.isApiError(err) ? err.message : "Ranking failed";
        setRankingError(msg);
        toast.error(msg);
        return null;
      } finally {
        setRankingLoading(false);
      }
    },
    [setSelectedJobId],
  );

  const scrollToSection = React.useCallback((id: string) => {
    setActiveSection(id);
    const section = document.getElementById(id);
    if (section) section.scrollIntoView({ behavior: "smooth", block: "start" });
  }, []);

  const selectedJob = React.useMemo(
    () => jobs.find((j) => j.id === selectedJobId) ?? null,
    [jobs, selectedJobId],
  );

  const value: AppContextValue = {
    backendStatus,
    backendVersion,
    apiBaseUrl: API_BASE_URL,
    jobs,
    jobsLoading,
    selectedJobId,
    setSelectedJobId,
    selectedJob,
    candidatesTotal,
    ranking,
    rankingLoading,
    rankingError,
    activity,
    refreshHealth,
    refreshJobs,
    refreshCandidatesTotal,
    refreshAll,
    runRanking,
    scrollToSection,
    activeSection,
    setActiveSection,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp(): AppContextValue {
  const ctx = React.useContext(AppContext);
  if (!ctx) throw new Error("useApp must be used within AppProvider");
  return ctx;
}

export function useLastTopN(): [number, (n: number) => void] {
  const [topN, setTopN] = React.useState(5);
  React.useEffect(() => {
    try {
      const n = parseInt(localStorage.getItem(LS_LAST_TOPN) || "5", 10);
      if (n >= 1 && n <= 20) setTopN(n);
    } catch {
      /* ignore */
    }
  }, []);
  const set = React.useCallback((n: number) => {
    setTopN(n);
    try {
      localStorage.setItem(LS_LAST_TOPN, String(n));
    } catch {
      /* ignore */
    }
  }, []);
  return [topN, set];
}