"use client";

import * as React from "react";
import {
  Users,
  FileText,
  Trophy,
  Award,
  ArrowRight,
  FilePlus2,
  ListChecks,
  Database,
  Activity as ActivityIcon,
  Clock,
  CalendarDays,
} from "lucide-react";
import { useApp } from "@/lib/app-context";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { formatNumber, formatDate } from "@/lib/utils";

interface Stat {
  label: string;
  value: string;
  sub?: string;
  icon: React.ComponentType<{ className?: string }>;
  tone: string;
}

export function DashboardOverview() {
  const { jobs, jobsLoading, candidatesTotal, activity, scrollToSection } = useApp();
  const latest = activity[0];

  const stats: Stat[] = [
    {
      label: "Total Candidates",
      value: formatNumber(candidatesTotal),
      sub: "In the screening pool",
      icon: Users,
      tone: "bg-violet-100 text-violet-700",
    },
    {
      label: "Total Job Descriptions",
      value: formatNumber(jobs.length),
      sub: "Open positions tracked",
      icon: FileText,
      tone: "bg-blue-100 text-blue-700",
    },
    {
      label: "Latest Ranking",
      value: latest?.jobTitle || "—",
      sub: latest ? `Top pick: ${latest.topCandidate}` : "Run your first ranking",
      icon: Trophy,
      tone: "bg-emerald-100 text-emerald-700",
    },
    {
      label: "Top Candidate Score",
      value: latest ? `${latest.topScore.toFixed(1)} / 100` : "—",
      sub: latest ? `Job #${latest.jobId}` : "No ranking data yet",
      icon: Award,
      tone: "bg-amber-100 text-amber-700",
    },
  ];

  return (
    <section id="dashboard" className="section-anchor space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-900">ResumeRank AI</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          AI-Powered Resume Screening and Candidate Ranking — hard filtering, BM25 + pgvector hybrid
          retrieval and explainable scoring in one workflow.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map((s) => {
          const Icon = s.icon;
          return (
            <Card key={s.label} className="overflow-hidden">
              <CardContent className="p-5">
                <div className="flex items-start justify-between">
                  <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${s.tone}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                </div>
                <p className="mt-4 text-2xl font-bold tracking-tight text-slate-900">{s.value}</p>
                <p className="text-sm font-medium text-slate-600">{s.label}</p>
                <p className="mt-0.5 text-xs text-muted-foreground">{s.sub}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader className="flex-row items-center justify-between space-y-0">
            <div className="space-y-1">
              <CardTitle className="flex items-center gap-2">
                <ActivityIcon className="h-4 w-4 text-primary" />
                Recent Activity
              </CardTitle>
              <CardDescription>Recently created jobs and executed rankings</CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="secondary">{formatNumber(candidatesTotal)} candidates</Badge>
              <Badge variant="secondary">{activity.length} rankings</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <p className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  <CalendarDays className="h-3.5 w-3.5" />
                  Recently created jobs
                </p>
                {jobsLoading ? (
                  <div className="space-y-2">
                    <Skeleton className="h-12 w-full" />
                    <Skeleton className="h-12 w-full" />
                  </div>
                ) : jobs.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No jobs created yet.</p>
                ) : (
                  <ul className="space-y-1.5">
                    {jobs.slice(0, 4).map((j) => (
                      <li
                        key={j.id}
                        className="flex items-center justify-between rounded-lg border px-3 py-2 text-sm"
                      >
                        <span className="min-w-0 truncate font-medium text-slate-700">{j.title}</span>
                        <span className="ml-2 shrink-0 text-xs text-muted-foreground">
                          {formatDate(j.created_at)}
                        </span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
              <div>
                <p className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  <Clock className="h-3.5 w-3.5" />
                  Recent rankings
                </p>
                {activity.length === 0 ? (
                  <p className="text-sm text-muted-foreground">
                    No rankings executed in this session yet. Run one to see it here.
                  </p>
                ) : (
                  <ul className="space-y-1.5">
                    {activity.slice(0, 4).map((a) => (
                      <li
                        key={`${a.jobId}-${a.timestamp}`}
                        className="flex items-center justify-between rounded-lg border px-3 py-2 text-sm"
                      >
                        <span className="min-w-0 truncate font-medium text-slate-700">{a.jobTitle}</span>
                        <span className="ml-2 shrink-0 text-xs text-emerald-700">
                          {a.topScore.toFixed(1)}
                        </span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Jump straight into the workflow</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2.5">
            <button
              type="button"
              onClick={() => scrollToSection("create-job")}
              className="group flex w-full items-center gap-3 rounded-lg border p-3 text-left transition-colors hover:border-primary/40 hover:bg-primary/5"
            >
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-blue-100 text-blue-700">
                <FilePlus2 className="h-4 w-4" />
              </span>
              <span className="min-w-0 flex-1">
                <span className="block text-sm font-semibold text-slate-800">Create Job Description</span>
                <span className="block text-xs text-muted-foreground">Add a new position to the ATS</span>
              </span>
              <ArrowRight className="h-4 w-4 text-muted-foreground transition-transform group-hover:translate-x-0.5" />
            </button>
            <button
              type="button"
              onClick={() => scrollToSection("rank")}
              className="group flex w-full items-center gap-3 rounded-lg border p-3 text-left transition-colors hover:border-primary/40 hover:bg-primary/5"
            >
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-violet-100 text-violet-700">
                <ListChecks className="h-4 w-4" />
              </span>
              <span className="min-w-0 flex-1">
                <span className="block text-sm font-semibold text-slate-800">Rank Candidates</span>
                <span className="block text-xs text-muted-foreground">Run the hybrid ranking pipeline</span>
              </span>
              <ArrowRight className="h-4 w-4 text-muted-foreground transition-transform group-hover:translate-x-0.5" />
            </button>
            <button
              type="button"
              onClick={() => scrollToSection("candidates")}
              className="group flex w-full items-center gap-3 rounded-lg border p-3 text-left transition-colors hover:border-primary/40 hover:bg-primary/5"
            >
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-emerald-100 text-emerald-700">
                <Database className="h-4 w-4" />
              </span>
              <span className="min-w-0 flex-1">
                <span className="block text-sm font-semibold text-slate-800">Candidate Database</span>
                <span className="block text-xs text-muted-foreground">Search and inspect all candidates</span>
              </span>
              <ArrowRight className="h-4 w-4 text-muted-foreground transition-transform group-hover:translate-x-0.5" />
            </button>
          </CardContent>
        </Card>
      </div>
      <Separator />
    </section>
  );
}