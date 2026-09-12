"use client";

import * as React from "react";
import { ChevronDown, Trophy, ExternalLink, FileText } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";
import type { RankingCandidateResult, ScoreBreakdown } from "@/lib/types";

interface Props {
  result: RankingCandidateResult;
  onViewProfile: (candidateId: number) => void;
}

function ScoreBar({ label, value }: { label: string; value: number | null | undefined }) {
  const v = Number(value) || 0;
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-[11px]">
        <span className="font-medium text-slate-600">{label}</span>
        <span className="font-mono font-semibold text-slate-800">{v.toFixed(1)}</span>
      </div>
      <Progress value={v} />
    </div>
  );
}

function LabeledValue({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="rounded-lg border bg-slate-50/60 px-2.5 py-1.5">
      <p className="text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">{label}</p>
      <p className="text-sm font-semibold text-slate-900">{value}</p>
    </div>
  );
}

export function ResultCard({ result, onViewProfile }: Props) {
  const [expanded, setExpanded] = React.useState(false);
  const bd: ScoreBreakdown | null | undefined = result.score_breakdown;
  const missingMandatory = bd?.missing_mandatory ?? [];
  const mandatoryOk = bd?.mandatory_skills_satisfied ?? result.missing_skills.length === 0;
  const isTop = result.rank === 1;

  return (
    <Card
      className={cn(
        "overflow-hidden transition-shadow",
        isTop ? "border-2 border-primary/70 shadow-[0_0_0_1px_hsl(var(--primary)/0.15),0_10px_30px_-8px_rgba(124,58,237,0.35)]" : "hover:shadow-md",
      )}
    >
      <CardContent className="p-0">
        <div className={cn("flex items-center gap-3 p-4", isTop && "bg-gradient-to-r from-violet-50 to-blue-50/40")}>
          <div
            className={cn(
              "flex h-11 w-11 shrink-0 items-center justify-center rounded-xl text-sm font-bold",
              isTop ? "bg-primary text-primary-foreground shadow-md shadow-primary/30" : "bg-secondary text-slate-700",
            )}
          >
            #{result.rank}
          </div>

          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="truncate font-semibold text-slate-900">{result.candidate_name || "Unknown"}</h3>
              {isTop && (
                <Badge variant="violet" className="items-center gap-1">
                  <Trophy className="h-3 w-3" /> Top match
                </Badge>
              )}
              {mandatoryOk ? (
                <Badge variant="success">All mandatory skills met</Badge>
              ) : (
                <Badge variant="destructive">{missingMandatory.length} missing mandatory</Badge>
              )}
            </div>
            <p className="mt-0.5 truncate text-xs text-muted-foreground">{result.experience_match}</p>
          </div>

          <div className="text-right">
            <p className="font-mono text-2xl font-bold text-slate-900">{result.match_score.toFixed(1)}</p>
            <p className="-mt-1 text-[10px] uppercase tracking-wide text-muted-foreground">final score</p>
          </div>
        </div>

        <div className="space-y-3 px-4 pb-4">
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="space-y-2.5">
              <ScoreBar label="Skills" value={result.skills_score} />
              <ScoreBar label="Experience" value={result.experience_score} />
              <ScoreBar label="Semantic" value={result.semantic_score} />
              <ScoreBar label="Education" value={result.education_score} />
            </div>
            <div className="grid grid-cols-2 gap-2 content-start sm:grid-cols-1 lg:grid-cols-2">
              <LabeledValue label="BM25" value={bd?.bm25_score?.toFixed?.(1) ?? "—"} />
              <LabeledValue label="Vector" value={bd?.vector_similarity_score?.toFixed?.(1) ?? "—"} />
              <LabeledValue label="Hybrid" value={bd?.hybrid_retrieval_score?.toFixed?.(1) ?? "—"} />
              <LabeledValue label="Final" value={bd?.final_score?.toFixed?.(1) ?? result.match_score.toFixed(1)} />
            </div>
          </div>

          {(result.matched_skills.length > 0 || result.missing_skills.length > 0) && (
            <Separator />
          )}

          {result.matched_skills.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {result.matched_skills.map((s) => (
                <Badge key={s} variant="success">
                  ✓ {s}
                </Badge>
              ))}
            </div>
          )}
          {missingMandatory.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {missingMandatory.map((s) => (
                <Badge key={s} variant="destructive">
                  ✕ {s}
                </Badge>
              ))}
            </div>
          )}

          {expanded && (
            <div className="space-y-3 rounded-lg border bg-slate-50/60 p-3 text-sm animate-fade-in">
              {result.career_summary && (
                <p className="leading-relaxed text-slate-700">
                  <span className="font-semibold text-slate-500">Summary: </span>
                  {result.career_summary}
                </p>
              )}
              {result.explanation && (
                <div className="rounded-lg border bg-white px-3 py-2.5">
                  <p className="text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">
                    Why this match
                  </p>
                  <p className="mt-1 text-slate-700">{result.explanation}</p>
                </div>
              )}
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
                <LabeledValue label="Skills" value={result.skills_score?.toFixed?.(1) ?? "—"} />
                <LabeledValue label="Experience" value={result.experience_score?.toFixed?.(1) ?? "—"} />
                <LabeledValue label="Semantic" value={result.semantic_score?.toFixed?.(1) ?? "—"} />
                <LabeledValue label="Education" value={result.education_score?.toFixed?.(1) ?? "—"} />
              </div>
            </div>
          )}

          <div className="flex flex-wrap items-center justify-between gap-2 border-t pt-3">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setExpanded((e) => !e)}
              aria-expanded={expanded}
            >
              <ChevronDown className={cn("h-3.5 w-3.5 transition-transform", expanded && "rotate-180")} />
              {expanded ? "Hide details" : "Score breakdown"}
            </Button>
            <Button
              variant={isTop ? "default" : "ghost"}
              size="sm"
              onClick={() => onViewProfile(result.candidate_id)}
            >
              <FileText className="h-3.5 w-3.5" />
              Full profile
              <ExternalLink className="h-3 w-3 opacity-60" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}