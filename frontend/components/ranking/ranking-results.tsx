"use client";

import * as React from "react";
import {
  ScrollText,
  Search,
  Filter,
  BarChart3,
  Users,
  Loader2,
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip as RechartTooltip,
  CartesianGrid,
  Cell,
} from "recharts";
import { useApp } from "@/lib/app-context";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { Button } from "@/components/ui/button";
import { ResultCard } from "@/components/ranking/result-card";
import { CandidateDetailDrawer } from "@/components/ranking/candidate-detail-drawer";
import { relaxationMode } from "@/lib/types";
import { RELAXATION_COLORS } from "@/lib/constants";
import { cn } from "@/lib/utils";
import type { RankingCandidateResult } from "@/lib/types";

export function RankingResults() {
  const { ranking, rankingLoading, rankingError, activity } = useApp();
  const [query, setQuery] = React.useState("");
  const [mandatoryOnly, setMandatoryOnly] = React.useState(false);
  const [sort, setSort] = React.useState<"score" | "name">("score");
  const [detailId, setDetailId] = React.useState<number | null>(null);

  const results = ranking?.top_candidates ?? [];
  const stats = ranking?.pipeline_stats;

  let visible: RankingCandidateResult[] = results;
  if (query.trim()) {
    const q = query.trim().toLowerCase();
    visible = visible.filter((r) => (r.candidate_name || "").toLowerCase().includes(q));
  }
  if (mandatoryOnly) {
    visible = visible.filter((r) => (r.score_breakdown?.missing_mandatory ?? []).length === 0);
  }
  if (sort === "name") {
    visible = [...visible].sort((a, b) =>
      (a.candidate_name || "").localeCompare(b.candidate_name || ""),
    );
  }

  const chartData = results.slice(0, 10).map((r) => ({
    name: r.rank,
    label: `${(r.candidate_name || "").split(" ")[0] ?? ""} #${r.rank}`,
    score: Number(r.match_score) || 0,
  }));

  const latestActivity = activity[0];
  const lastJobWithResults =
    ranking ?? (latestActivity ? { job_id: latestActivity.jobId, job_title: latestActivity.jobTitle } : null);

  const relax = stats ? relaxationMode(stats) : null;

  return (
    <section id="results" className="section-anchor">
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
          <ScrollText className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-lg font-bold tracking-tight text-slate-900">Ranking Results</h2>
          <p className="text-xs text-muted-foreground">
            {lastJobWithResults
              ? `${lastJobWithResults.job_title} · ${results.length} in the Top-N shown below`
              : "Results from the latest ranking run appear here"}
          </p>
        </div>
      </div>

      {rankingLoading ? (
        <div className="space-y-3">
          <Skeleton className="h-12 w-full" />
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-40 w-full" />
          ))}
        </div>
      ) : rankingError ? (
        <EmptyState
          icon={Users}
          title="Ranking failed"
          description={rankingError}
          action={
            <Badge variant="destructive">Check that the backend is running and reachable</Badge>
          }
        />
      ) : !ranking ? (
        <EmptyState
          icon={BarChart3}
          title="No ranking results yet"
          description="Select a job in the ranking section above and click Rank Candidates to see explainable results here."
        />
      ) : results.length === 0 ? (
        <Card>
          <CardContent className="space-y-4 p-6">
            <EmptyState
              icon={Users}
              title="No candidates could be ranked"
              description="The pipeline ran but produced zero final candidates. Review the debug statistics below."
            />
            {stats && (
              <div className="grid gap-3 rounded-lg border bg-slate-50/60 p-4 text-sm sm:grid-cols-3">
                <div>
                  <p className="text-xs text-muted-foreground">Candidates evaluated</p>
                  <p className="text-lg font-bold text-slate-900">{stats.total_candidates_evaluated}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Passed hard filter</p>
                  <p className="text-lg font-bold text-slate-900">{stats.hard_filtered}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Final ranked</p>
                  <p className="text-lg font-bold text-slate-900">{stats.final_ranked}</p>
                </div>
                {relax && stats.relaxation_reason && (
                  <div className="sm:col-span-3 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
                    <span className="font-semibold">
                      Relaxation mode: <Badge className="ml-1" variant={RELAXATION_COLORS[relax.mode]}>{relax.label}</Badge>
                    </span>{" "}
                    · {stats.relaxation_reason}
                  </div>
                )}
                {!stats.relaxation_reason && stats.total_candidates_evaluated === 0 && (
                  <p className="sm:col-span-3 text-xs text-muted-foreground">
                    The candidate database is empty — upload resumes in the Candidate Database section, then re-run.
                  </p>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          <Card>
            <CardContent className="space-y-4 p-4">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    placeholder="Search candidate…"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="pl-9"
                  />
                </div>
                <Button
                  variant={mandatoryOnly ? "default" : "outline"}
                  size="sm"
                  onClick={() => setMandatoryOnly((v) => !v)}
                >
                  <Filter className="h-3.5 w-3.5" />
                  Mandatory met only
                </Button>
                <Select
                  value={sort}
                  onChange={(e) => setSort(e.target.value as "score" | "name")}
                  className="sm:w-44"
                >
                  <option value="score">Sort: final score</option>
                  <option value="name">Sort: name A-Z</option>
                </Select>
              </div>

              <div>
                <p className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  <BarChart3 className="h-3.5 w-3.5" /> Final scores · Top {chartData.length}
                </p>
                <div className="h-36 w-full rounded-lg border bg-white">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData} margin={{ top: 8, right: 8, left: -22, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                      <XAxis dataKey="name" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                      <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                      <RechartTooltip
                        cursor={{ fill: "rgba(124,58,237,0.06)" }}
                        formatter={(value, _name) => {
                          const v = Array.isArray(value) ? value[0] : value;
                          return [`${Number(v ?? 0).toFixed(1)} / 100`, "Final score"];
                        }}
                        labelFormatter={(label) => `Rank #${label}`}
                        contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #e2e8f0" }}
                      />
                      <Bar dataKey="score" radius={[5, 5, 0, 0]} maxBarSize={44}>
                        {chartData.map((d, i) => (
                          <Cell key={i} fill={i === 0 ? "hsl(262 83% 58%)" : "hsl(221 83% 55%)"} fillOpacity={i === 0 ? 1 : 0.55} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                <span>
                  Showing <strong className="text-slate-700">{visible.length}</strong> of{" "}
                  <strong className="text-slate-700">{results.length}</strong> candidates
                </span>
                <Badge variant="secondary">Filter by name or mandatory-skill match</Badge>
              </div>
            </CardContent>
          </Card>

          <div className={cn("grid gap-4 lg:grid-cols-2")}>
            {visible.map((r) => (
              <ResultCard key={r.candidate_id} result={r} onViewProfile={setDetailId} />
            ))}
          </div>

          {visible.length === 0 && (
            <EmptyState
              icon={Search}
              title="No candidates match your filters"
              description="Try clearing the search or turning off the mandatory-skill filter."
              compact
            />
          )}
        </div>
      )}

      <CandidateDetailDrawer candidateId={detailId} onClose={() => setDetailId(null)} />
    </section>
  );
}