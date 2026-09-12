import {
  LayoutDashboard,
  FilePlus2,
  ListChecks,
  ScrollText,
  Users,
  type LucideIcon,
} from "lucide-react";

export const APP_NAME = "ResumeRank AI";
export const APP_TAGLINE = "AI-Powered Resume Screening and Candidate Ranking";
export const APP_VERSION = "1.0.0";

export interface NavItem {
  id: string;
  label: string;
  icon: LucideIcon;
  sectionId: string;
}

export const NAV_ITEMS: NavItem[] = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard, sectionId: "dashboard" },
  { id: "create-job", label: "Create Job", icon: FilePlus2, sectionId: "create-job" },
  { id: "rank", label: "Rank Candidates", icon: ListChecks, sectionId: "rank" },
  { id: "results", label: "Ranking Results", icon: ScrollText, sectionId: "results" },
  { id: "candidates", label: "Candidate Database", icon: Users, sectionId: "candidates" },
];

export const SECTION_IDS = NAV_ITEMS.map((n) => n.sectionId);

export const SENIORITY_LEVELS = ["Junior", "Mid-Level", "Senior", "Lead", "Manager"] as const;

export const RELAXATION_COLORS: Record<string, "success" | "info" | "warning" | "destructive" | "default"> = {
  strict: "success",
  relaxed_mandatory: "info",
  relaxed_all: "warning",
  baseline: "destructive",
  none: "default",
};

export const PAGE_META: Record<string, { title: string; description: string }> = {
  dashboard: {
    title: "Dashboard",
    description: "Overview of candidates, jobs and recent ranking activity",
  },
  "create-job": {
    title: "Create Job Description",
    description: "Add a job description to your ATS and prepare it for candidate matching",
  },
  rank: {
    title: "Rank Candidates",
    description: "Run the hybrid ranking pipeline against a job description",
  },
  results: {
    title: "Ranking Results",
    description: "Inspect scores, skill matches and breakdowns for the top candidates",
  },
  candidates: {
    title: "Candidate Database",
    description: "Search, upload and inspect every candidate in the system",
  },
};