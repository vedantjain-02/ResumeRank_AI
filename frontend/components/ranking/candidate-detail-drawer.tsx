"use client";

import * as React from "react";
import {
  Phone,
  Clock,
  BadgeCheck,
  GraduationCap,
  Award,
  Users,
  FileText,
  Star,
  Loader2,
} from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { fetchCandidate, ApiError } from "@/lib/api";
import type { CandidateDetail, RankingCandidateResult } from "@/lib/types";
import { yearLabel, titleCase } from "@/lib/utils";

interface Props {
  candidateId: number | null;
  rankInfo?: RankingCandidateResult | null;
  onClose: () => void;
}

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="rounded-lg border bg-slate-50/60 p-3">
      <p className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">{label}</p>
      <div className="mt-1 text-sm text-slate-800">{value}</div>
    </div>
  );
}

export function CandidateDetailDrawer({ candidateId, rankInfo, onClose }: Props) {
  const [candidate, setCandidate] = React.useState<CandidateDetail | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (candidateId == null) {
      setCandidate(null);
      setError(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchCandidate(candidateId)
      .then((c) => {
        if (!cancelled) setCandidate(c);
      })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof ApiError ? err.message : "Failed to load candidate");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [candidateId]);

  return (
    <Dialog
      open={candidateId != null}
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
    >
      <DialogContent side="right" className="scrollbar-thin overflow-y-auto">
        <DialogHeader className="border-b px-5 py-4">
          {loading ? (
            <DialogTitle>Loading profile…</DialogTitle>
          ) : candidate ? (
            <>
              <div className="flex items-center gap-2">
                <DialogTitle className="text-slate-900">{candidate.name || "Unnamed candidate"}</DialogTitle>
                {candidate.is_seed && <Badge variant="secondary">Seed</Badge>}
              </div>
              <DialogDescription>
                {candidate.job_title || "Role not specified"} · {yearLabel(candidate.total_experience_years)}
              </DialogDescription>
            </>
          ) : (
            <DialogTitle>Candidate profile</DialogTitle>
          )}
        </DialogHeader>

        {rankInfo && (
          <div className="space-y-3 border-b px-5 py-4">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-full bg-primary/10 text-primary">
                <Star className="h-5 w-5 fill-primary text-primary" />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-900">
                  Rank #{rankInfo.rank} · Final score {rankInfo.match_score.toFixed(1)}
                </p>
                <p className="text-xs text-muted-foreground">{rankInfo.experience_match}</p>
              </div>
            </div>
            {rankInfo.matched_skills.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {rankInfo.matched_skills.map((s) => (
                  <Badge key={s} variant="success">
                    ✓ {s}
                  </Badge>
                ))}
              </div>
            )}
            {rankInfo.missing_skills.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {rankInfo.missing_skills.map((s) => (
                  <Badge key={s} variant="destructive">
                    ✕ {s}
                  </Badge>
                ))}
              </div>
            )}
          </div>
        )}

        <div className="space-y-3 px-5 py-4">
          {loading && (
            <div className="space-y-3">
              <Skeleton className="h-16 w-full" />
              <Skeleton className="h-24 w-full" />
              <Skeleton className="h-16 w-full" />
            </div>
          )}

          {error && (
            <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>
          )}

          {candidate && !loading && (
            <>
              <div className="grid gap-3 sm:grid-cols-2">
                <Field
                  label="Experience"
                  value={
                    <span className="flex items-center gap-1.5">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      {yearLabel(candidate.total_experience_years)}
                    </span>
                  }
                />
                <Field
                  label="Seniority"
                  value={
                    <span className="flex items-center gap-1.5">
                      <Award className="h-4 w-4 text-muted-foreground" />
                      {titleCase(candidate.seniority_level)}
                    </span>
                  }
                />
              </div>

              {candidate.phone_number && (
                <Field
                  label="Phone"
                  value={
                    <span className="flex items-center gap-1.5">
                      <Phone className="h-4 w-4 text-muted-foreground" />
                      {candidate.phone_number}
                    </span>
                  }
                />
              )}

              {candidate.career_summary && (
                <Field label="Career summary" value={<p className="leading-relaxed">{candidate.career_summary}</p>} />
              )}

              {candidate.capability_tags.length > 0 && (
                <div>
                  <p className="mb-2 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                    <BadgeCheck className="h-3.5 w-3.5" /> Capability tags
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {candidate.capability_tags.map((t) => (
                      <Badge key={t} variant="default">
                        {t}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {candidate.functional_expertise && candidate.functional_expertise.length > 0 && (
                <>
                  <Separator />
                  <p className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                    <Users className="h-3.5 w-3.5" /> Functional expertise
                  </p>
                  <div className="space-y-1.5">
                    {candidate.functional_expertise.map((f, i) => (
                      <div key={i} className="flex items-start justify-between gap-2 rounded-lg border px-3 py-2 text-sm">
                        <span className="font-medium text-slate-800">{f.area}</span>
                        <span className="shrink-0 text-xs text-muted-foreground">
                          {f.years != null ? `${f.years} yrs` : "—"}
                        </span>
                      </div>
                    ))}
                  </div>
                </>
              )}

              {candidate.education && candidate.education.length > 0 && (
                <>
                  <Separator />
                  <p className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                    <GraduationCap className="h-3.5 w-3.5" /> Education
                  </p>
                  <div className="space-y-1.5">
                    {candidate.education.map((e, i) => (
                      <div key={i} className="rounded-lg border px-3 py-2 text-sm">
                        <p className="font-medium text-slate-800">
                          {[e.degree, e.field].filter(Boolean).join(" · ") || "—"}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {e.institution && <span>{e.institution}</span>}
                          {e.graduation_year && <span>{e.institution ? " · " : ""}{e.graduation_year}</span>}
                        </p>
                      </div>
                    ))}
                  </div>
                </>
              )}

              {candidate.resume_text && (
                <>
                  <Separator />
                  <p className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                    <FileText className="h-3.5 w-3.5" /> Resume text preview
                  </p>
                  <details className="rounded-lg border bg-slate-50/60 p-3">
                    <summary className="cursor-pointer text-xs font-medium text-slate-600 hover:text-slate-900">
                      Show resume text
                    </summary>
                    <pre className="mt-2 max-h-72 overflow-y-auto whitespace-pre-wrap font-mono text-xs leading-relaxed text-slate-700 scrollbar-thin">
                      {candidate.resume_text}
                    </pre>
                  </details>
                </>
              )}
            </>
          )}

          {!candidate && !loading && !error && (
            <p className="py-6 text-center text-sm text-muted-foreground">Select a candidate to view their profile.</p>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}