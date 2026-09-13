"use client";

import * as React from "react";
import {
  Users,
  Filter,
  Search,
  Layers,
  GitMerge,
  Trophy,
  Scale,
  CalendarRange,
  BadgeCheck,
  ThumbsUp,
  Lightbulb,
  Info,
  SlidersHorizontal,
  Target,
  UserPlus,
} from "lucide-react";
import { useApp } from "@/lib/app-context";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { relaxationMode, type PipelineStats } from "@/lib/types";
import { RELAXATION_COLORS } from "@/lib/constants";
import { formatNumber } from "@/lib/utils";
import { cn } from "@/lib/utils";

function StatTile({
  label,
  value,
  icon: Icon,
  hint,
}: {
  label: string;
  value: string;
  icon: React.ComponentType<{ className?: string }>;
  hint?: string;
}) {
  const body = (
    <div className="rounded-lg border bg-slate-50/60 p-3">
      <p className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
        <Icon className="h-3.5 w-3.5" />
        {label}
      </p>
      <p className="mt-1 text-lg font-bold text-slate-900">{value}</p>
    </div>
  );
  if (!hint) return body;
  return (
    <Tooltip>
      <TooltipTrigger asChild>{body}</TooltipTrigger>
      <TooltipContent className="max-w-[260px]">{hint}</TooltipContent>
    </Tooltip>
  );
}

function SkillChips({ skills, icon: Icon, title }: { skills: string[]; icon: React.ComponentType<{ className?: string }>; title: string }) {
  return (
    <div className="rounded-lg border bg-slate-50/60 p-3">
      <p className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
        <Icon className="h-3.5 w-3.5" />
        {title}
      </p>
      {skills.length === 0 ? (
        <p className="mt-1 text-xs text-muted-foreground">None parsed</p>
      ) : (
        <div className="mt-1.5 flex flex-wrap gap-1.5">
          {skills.slice(0, 20).map((s) => (
            <Badge key={s}>{s}</Badge>
          ))}
          {skills.length > 20 && <Badge variant="secondary">+{skills.length - 20}</Badge>}
        </div>
      )}
    </div>
  );
}

export function PipelineStatsPanel() {
  const { ranking, rankingLoading } = useApp();
  const stats: PipelineStats | null | undefined = ranking?.pipeline_stats;

  if (!rankingLoading && !stats) return null;
  if (!stats) {
    return (
      <Card className="mt-4">
        <CardContent className="p-5 text-sm text-muted-foreground">
          Pipeline statistics appear here after a ranking completes.
        </CardContent>
      </Card>
    );
  }

  const relax = relaxationMode(stats);
  const conditions = stats.hard_filter_conditions ?? [];
  const attempts = stats.hard_filter_attempts ?? [];

  return (
    <Card className="mt-4 animate-fade-in">
      <CardHeader>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <CardTitle className="flex items-center gap-2 text-base">
              <SlidersHorizontal className="h-4 w-4 text-primary" />
              Pipeline Statistics
            </CardTitle>
            <CardDescription>
              Hard filter → BM25 + pgvector → fusion → detailed ranking
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-muted-foreground">Relaxation mode:</span>
            <Badge variant={RELAXATION_COLORS[relax.mode] ?? "default"} className="px-3 py-1 text-xs">
              {relax.label}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {relax.reason && (
          <div className="flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800 animate-fade-in">
            <Info className="mt-0.5 h-3.5 w-3.5 shrink-0" />
            <p>
              <strong>Relaxation reason:</strong> {relax.reason}
            </p>
          </div>
        )}

        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
          <StatTile
            label="Selected limit"
            value={formatNumber(stats.selected_limit ?? stats.final_ranked)}
            icon={Target}
            hint="The Top-N requested for this ranking run."
          />
          <StatTile
            label="Total evaluated"
            value={formatNumber(stats.total_candidates_evaluated)}
            icon={Users}
            hint="Every candidate in the database that entered the pipeline."
          />
          <StatTile
            label="Strict filtered"
            value={formatNumber(stats.strict_hard_filtered ?? stats.hard_filtered)}
            icon={Filter}
            hint="Candidates that passed every strict hard filter (mandatory skills, seniority, education, experience bounds)."
          />
          <StatTile
            label="Relaxed fill-ins"
            value={formatNumber(stats.relaxed_candidates ?? 0)}
            icon={UserPlus}
            hint="Candidates added from progressively relaxed filters so the requested limit can be filled."
          />
          <StatTile
            label="BM25 retrieved"
            value={formatNumber(stats.bm25_retrieved)}
            icon={Search}
            hint="Candidates retrieved by the BM25 lexical search stage."
          />
          <StatTile
            label="Vector retrieved"
            value={formatNumber(stats.vector_retrieved)}
            icon={Layers}
            hint="Candidates retrieved by the pgvector semantic search stage."
          />
          <StatTile
            label="Hybrid pool"
            value={formatNumber(stats.fused_pool)}
            icon={GitMerge}
            hint="Post-fusion pool passed to detailed explainable scoring."
          />
          <StatTile
            label="Final ranked"
            value={formatNumber(stats.final_ranked)}
            icon={Trophy}
            hint="Candidates in the final Top-N result."
          />
          <StatTile
            label="Max experience"
            value={
              stats.maximum_experience != null
                ? `${stats.maximum_experience} yrs`
                : "Unlimited"
            }
            icon={CalendarRange}
            hint="Upper experience bound parsed from the JD and applied as a hard filter (never relaxed)."
          />
          <StatTile
            label="Hard filter cap"
            value={formatNumber(stats.hard_filter_limit)}
            icon={Scale}
            hint="Maximum pool size kept after the hard-filter stage."
          />
        </div>

        <div className="flex flex-wrap items-center gap-2 rounded-lg border bg-slate-50/60 px-3 py-2.5 text-xs text-muted-foreground">
          <span className="font-semibold text-slate-600">Weights:</span>
          <Badge variant="secondary">BM25 {stats.bm25_weight?.toFixed?.(2) ?? "—"}</Badge>
          <Badge variant="secondary">Vector {stats.vector_weight?.toFixed?.(2) ?? "—"}</Badge>
          <Badge variant="secondary">Hybrid {stats.final_hybrid_weight?.toFixed?.(2) ?? "—"}</Badge>
          <Badge variant="secondary">Detailed {stats.final_detailed_weight?.toFixed?.(2) ?? "—"}</Badge>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <SkillChips skills={stats.parsed_mandatory_skills ?? []} icon={BadgeCheck} title="Parsed mandatory skills" />
          <SkillChips skills={stats.parsed_preferred_skills ?? []} icon={ThumbsUp} title="Parsed preferred skills" />
          <SkillChips skills={stats.parsed_inferred_skills ?? []} icon={Lightbulb} title="Parsed inferred skills" />
        </div>

        {conditions.length > 0 && (
          <div className="rounded-lg border bg-slate-50/60 p-3">
            <p className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
              Hard filter conditions
            </p>
            <div className="mt-1.5 flex flex-wrap gap-1.5">
              {conditions.map((c) => (
                <Badge key={c} variant="outline">
                  {c}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {attempts.length > 0 && (
          <div className="rounded-lg border bg-slate-50/60 p-3">
            <p className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
              Relaxation cascade attempts
            </p>
            <div className="mt-2 space-y-1.5">
              {attempts.map((a, i) => {
                const last = i === attempts.length - 1;
                return (
                  <div key={`${a.level}-${i}`} className="flex items-center gap-2 text-xs">
                    <span
                      className={cn(
                        "inline-flex w-40 shrink-0 items-center rounded-md px-2 py-1 font-semibold",
                        last
                          ? "bg-emerald-100 text-emerald-800"
                          : "bg-slate-200 text-slate-600",
                      )}
                    >
                      {a.level}
                    </span>
                    <span className="font-medium text-slate-700">pool: {a.pool_size}</span>
                    {a.additions != null && (
                      <span className="text-muted-foreground">· +{a.additions} added</span>
                    )}
                    {a.mandatory_skills != null && (
                      <span className="text-muted-foreground">· mandatory: {a.mandatory_skills}</span>
                    )}
                    {last && <Badge variant="success">selected</Badge>}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}