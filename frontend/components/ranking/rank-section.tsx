"use client";

import * as React from "react";
import {
  ListChecks,
  Loader2,
  Sparkles,
  Users,
  GraduationCap,
  BadgeCheck,
  ThumbsUp,
  Clock,
} from "lucide-react";
import { useApp, useLastTopN } from "@/lib/app-context";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { formatNumber, toSkillList, yearLabel } from "@/lib/utils";
import { PipelineStatsPanel } from "@/components/ranking/pipeline-stats";

function SkillChips({ skills, tone }: { skills: string[]; tone: "default" | "outline" }) {
  if (skills.length === 0) return <span className="text-xs text-muted-foreground">None</span>;
  return (
    <div className="flex flex-wrap gap-1.5">
      {skills.slice(0, 24).map((s) => (
        <Badge key={s} variant={tone}>
          {s}
        </Badge>
      ))}
      {skills.length > 24 && (
        <Badge variant="secondary">+{skills.length - 24} more</Badge>
      )}
    </div>
  );
}

export function RankSection() {
  const {
    jobs,
    jobsLoading,
    selectedJobId,
    setSelectedJobId,
    selectedJob,
    candidatesTotal,
    rankingLoading,
    ranking,
    rankingError,
    runRanking,
    scrollToSection,
  } = useApp();
  const [topN, setTopN] = useLastTopN();

  const onRank = async () => {
    if (!selectedJobId || rankingLoading) return;
    await runRanking(selectedJobId, topN);
    scrollToSection("results");
  };

  const required = toSkillList(selectedJob?.required_skills);
  const preferred = toSkillList(selectedJob?.preferred_skills);
  const mandatory = toSkillList(selectedJob?.is_mandatory_requirements);

  return (
    <section id="rank" className="section-anchor">
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
          <ListChecks className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-lg font-bold tracking-tight text-slate-900">Rank Candidates for a Job</h2>
          <p className="text-xs text-muted-foreground">
            Hard filtering → BM25 + pgvector → hybrid fusion → detailed explainable scoring
          </p>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-5">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base">Ranking Controls</CardTitle>
            <CardDescription>Pick a job and run the pipeline</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="rank-job">Job description</Label>
              <Select
                id="rank-job"
                value={selectedJobId != null ? String(selectedJobId) : ""}
                onChange={(e) => setSelectedJobId(e.target.value ? parseInt(e.target.value, 10) : null)}
                disabled={jobsLoading}
              >
                <option value="">{jobsLoading ? "Loading jobs…" : "Select a job…"}</option>
                {jobs.map((j) => (
                  <option key={j.id} value={j.id}>
                    #{j.id} · {j.title}
                  </option>
                ))}
              </Select>
              {jobs.length === 0 && !jobsLoading && (
                <p className="text-xs text-muted-foreground">
                  No jobs yet -{" "}
                  <button
                    type="button"
                    className="font-semibold text-primary underline-offset-2 hover:underline"
                    onClick={() => scrollToSection("create-job")}
                  >
                    create one first
                  </button>
                </p>
              )}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="rank-topn">Number of candidates</Label>
              <Select id="rank-topn" value={String(topN)} onChange={(e) => setTopN(parseInt(e.target.value, 10))}>
                {[5, 10, 15, 20].map((n) => (
                  <option key={n} value={n}>
                    Top {n}
                  </option>
                ))}
              </Select>
            </div>

            <Button
              type="button"
              size="lg"
              className="w-full"
              onClick={onRank}
              disabled={!selectedJobId || rankingLoading || jobsLoading}
            >
              {rankingLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Sparkles className="h-4 w-4" />
              )}
              {rankingLoading ? "Ranking…" : "Rank Candidates"}
            </Button>

            {rankingLoading && (
              <div className="rounded-lg border bg-primary/5 p-3 text-xs text-muted-foreground animate-fade-in">
                <p className="font-medium text-slate-700">Running the hybrid pipeline…</p>
                <p className="mt-1">
                  Hard filtering → BM25 + pgvector retrieval → hybrid fusion → detailed scoring → Top {topN}.
                </p>
                <div className="mt-2 h-1 w-full overflow-hidden rounded-full bg-slate-200">
                  <div className="h-full w-1/2 animate-pulse rounded-full bg-primary" />
                </div>
              </div>
            )}

            {rankingError && !rankingLoading && (
              <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700 animate-fade-in">
                {rankingError}
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle className="text-base">Selected Job</CardTitle>
            <CardDescription>Context used for matching</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {!selectedJob ? (
              <EmptyState
                icon={ListChecks}
                title="No job selected"
                description="Choose a job description above to see its requirements and run a ranking."
                compact
              />
            ) : (
              <>
                <div className="flex flex-wrap items-center gap-2">
                  <Badge variant="navy">#{selectedJob.id}</Badge>
                  <h3 className="text-base font-semibold text-slate-900">{selectedJob.title}</h3>
                  <span className="text-xs text-muted-foreground">
                    {formatNumber(candidatesTotal)} candidates available in the database
                  </span>
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <div className="rounded-lg border bg-slate-50/60 p-3">
                    <p className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                      <Clock className="h-3.5 w-3.5" /> Experience range
                    </p>
                    <p className="text-sm font-medium text-slate-800">
                      Min {yearLabel(selectedJob.minimum_experience ?? 0)}
                      <span className="mx-1.5 text-muted-foreground">·</span>
                      {selectedJob.education_requirement ? (
                        <>
                          <GraduationCap className="mb-0.5 inline h-3.5 w-3.5 text-violet-600" />{" "}
                          <span className="font-normal text-slate-700">{selectedJob.education_requirement}</span>
                        </>
                      ) : (
                        "Education not specified"
                      )}
                    </p>
                  </div>
                  <div className="rounded-lg border bg-slate-50/60 p-3">
                    <p className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                      <Users className="h-3.5 w-3.5" /> Experience fit signal
                    </p>
                    <p className="text-sm font-medium text-slate-800">
                      {toSkillList(selectedJob.certifications_required).length > 0
                        ? `Certifications: ${selectedJob.certifications_required}`
                        : "No certifications listed"}
                    </p>
                  </div>
                </div>

                <div className="space-y-1.5">
                  <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                    <BadgeCheck className="h-3.5 w-3.5" /> Required / mandatory skills
                  </p>
                  <SkillChips skills={mandatory.length ? mandatory : required} tone="default" />
                </div>

                <div className="space-y-1.5">
                  <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                    <ThumbsUp className="h-3.5 w-3.5" /> Preferred skills
                  </p>
                  <SkillChips skills={preferred} tone="outline" />
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      <PipelineStatsPanel />
    </section>
  );
}