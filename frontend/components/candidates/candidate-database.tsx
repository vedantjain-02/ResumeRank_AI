"use client";

import * as React from "react";
import {
  Users,
  ChevronDown,
  Search,
  Upload,
  Loader2,
  Eye,
  GraduationCap,
} from "lucide-react";
import { toast } from "sonner";
import { useApp } from "@/lib/app-context";
import {
  fetchCandidates,
  uploadResume,
  ApiError,
} from "@/lib/api";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { CandidateDetailDrawer } from "@/components/ranking/candidate-detail-drawer";
import { formatNumber, yearLabel, cn, debounce } from "@/lib/utils";
import type { Candidate } from "@/lib/types";

const PAGE_SIZE = 12;

export function CandidateDatabase() {
  const { candidatesTotal, refreshCandidatesTotal, scrollToSection } = useApp();
  const [open, setOpen] = React.useState(false);
  const [candidates, setCandidates] = React.useState<Candidate[]>([]);
  const [total, setTotal] = React.useState(0);
  const [loading, setLoading] = React.useState(false);
  const [page, setPage] = React.useState(0);
  const [search, setSearch] = React.useState("");
  const [seniority, setSeniority] = React.useState("");
  const [minExp, setMinExp] = React.useState("");
  const [sort, setSort] = React.useState<"newest" | "name" | "exp">("newest");
  const [detailId, setDetailId] = React.useState<number | null>(null);
  const [uploading, setUploading] = React.useState(false);
  const [file, setFile] = React.useState<File | null>(null);

  const load = React.useCallback(
    async (opts?: { searchQuery?: string; seniorityLevel?: string; minExperience?: string; page?: number; reset?: boolean }) => {
      setLoading(true);
      try {
        const nextPage = opts?.reset ? 0 : opts?.page ?? page;
        setPage(nextPage);
        const res = await fetchCandidates({
          search: opts?.searchQuery !== undefined ? opts.searchQuery : search,
          seniority_level: opts?.seniorityLevel !== undefined ? opts.seniorityLevel : seniority,
          min_experience: opts?.minExperience !== undefined && opts.minExperience !== "" ? Number(opts.minExperience) : undefined,
          limit: PAGE_SIZE,
          offset: nextPage * PAGE_SIZE,
        });
        setCandidates(res.candidates);
        setTotal(res.total);
      } catch (err) {
        toast.error(err instanceof ApiError ? err.message : "Could not load candidates");
      } finally {
        setLoading(false);
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [page, search, seniority, minExp],
  );

  const debouncedSearch = React.useMemo(
    () => debounce((value: string) => load({ searchQuery: value, reset: true }), 320),
    [load],
  );

  React.useEffect(() => {
    if (open) load({ reset: true });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  React.useEffect(() => {
    void refreshCandidatesTotal();
  }, [refreshCandidatesTotal]);

  const onUpload = async () => {
    if (!file) {
      toast.error("Choose a resume file first (.pdf or .docx)");
      return;
    }
    setUploading(true);
    try {
      const res = await uploadResume(file);
      toast.success("Resume processed", {
        description: `${res.name || `Candidate #${res.id}`} added to the database.`,
      });
      setFile(null);
      await load({ reset: true });
      await refreshCandidatesTotal();
      scrollToSection("candidates");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const sorted = React.useMemo(() => {
    const list = [...candidates];
    if (sort === "name") list.sort((a, b) => (a.name || "").localeCompare(b.name || ""));
    else if (sort === "exp") list.sort((a, b) => (b.total_experience_years ?? 0) - (a.total_experience_years ?? 0));
    else list.sort((a, b) => (b.id ?? 0) - (a.id ?? 0));
    return list;
  }, [candidates, sort]);

  const pages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const start = page * PAGE_SIZE + 1;
  const end = Math.min(page * PAGE_SIZE + PAGE_SIZE, total);

  return (
    <section id="candidates" className="section-anchor">
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
          <Users className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-lg font-bold tracking-tight text-slate-900">Candidate Database</h2>
          <p className="text-xs text-muted-foreground">Search, filter, upload and inspect every candidate</p>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <Badge variant="secondary" className="px-3 py-1">
            {formatNumber(candidatesTotal)} candidates
          </Badge>
          <Button variant="outline" size="sm" onClick={() => setOpen((o) => !o)} aria-expanded={open}>
            {open ? "Collapse" : "Expand"}
            <ChevronDown className={cn("h-3.5 w-3.5 transition-transform", open && "rotate-180")} />
          </Button>
        </div>
      </div>

      {!open && (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-dashed bg-slate-50/60 px-5 py-4">
          <p className="text-sm text-muted-foreground">
            The full candidate table is collapsed.{" "}
            <strong className="text-slate-700">Expand</strong> to search, upload and inspect candidates.
          </p>
          <div className="flex gap-2">
            <Badge variant="secondary">{formatNumber(candidatesTotal)} total</Badge>
            <Badge variant="secondary">12 per page</Badge>
          </div>
        </div>
      )}

      {open && (
        <div className="space-y-4 animate-fade-in">
          <div className="grid gap-4 lg:grid-cols-[minmax(260px,360px)_1fr]">
            <Card>
              <CardHeader className="pb-3">
                <p className="flex items-center gap-1.5 text-sm font-semibold text-slate-800">
                  <Upload className="h-4 w-4 text-primary" />
                  Upload a resume
                </p>
              </CardHeader>
              <CardContent className="space-y-3">
                <label
                  htmlFor="cand-upload"
                  className="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed px-4 py-6 text-center transition-colors hover:border-primary/50 hover:bg-primary/5"
                >
                  <Upload className="h-5 w-5 text-muted-foreground" />
                  <span className="text-xs font-medium text-slate-700">
                    {file ? file.name : "Choose a resume (.pdf, .docx)"}
                  </span>
                  {file && <span className="text-[11px] text-muted-foreground">{(file.size / 1024).toFixed(1)} KB</span>}
                  <input
                    id="cand-upload"
                    type="file"
                    accept=".pdf,.docx"
                    className="sr-only"
                    onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                  />
                </label>
                <Button className="w-full" onClick={onUpload} disabled={uploading}>
                  {uploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
                  {uploading ? "Processing…" : "Upload & Process"}
                </Button>
                <p className="text-[11px] leading-relaxed text-muted-foreground">
                  The backend extracts structured profile data and generates a pgvector embedding automatically.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <p className="flex items-center gap-1.5 text-sm font-semibold text-slate-800">
                  <Search className="h-4 w-4 text-primary" />
                  Search &amp; filters
                </p>
              </CardHeader>
              <CardContent className="space-y-3">
                <Input
                  placeholder="Search name, title, skills, summary…"
                  value={search}
                  onChange={(e) => {
                    setSearch(e.target.value);
                    debouncedSearch(e.target.value);
                  }}
                />
                <div className="grid gap-3 sm:grid-cols-3">
                  <Select value={seniority} onChange={(e) => { setSeniority(e.target.value); load({ seniorityLevel: e.target.value, reset: true }); }}>
                    <option value="">All seniority</option>
                    <option>Junior</option>
                    <option>Mid-Level</option>
                    <option>Senior</option>
                    <option>Lead</option>
                    <option>Manager</option>
                  </Select>
                  <Select value={minExp} onChange={(e) => { setMinExp(e.target.value); load({ minExperience: e.target.value, reset: true }); }}>
                    <option value="">Any experience</option>
                    <option value="2">2+ years</option>
                    <option value="4">4+ years</option>
                    <option value="6">6+ years</option>
                    <option value="8">8+ years</option>
                    <option value="10">10+ years</option>
                  </Select>
                  <Select value={sort} onChange={(e) => setSort(e.target.value as typeof sort)}>
                    <option value="newest">Newest first</option>
                    <option value="name">Name A-Z</option>
                    <option value="exp">Most experienced</option>
                  </Select>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardContent className="p-0">
              {loading && candidates.length === 0 ? (
                <div className="space-y-3 p-5">
                  <Skeleton className="h-10 w-full" />
                  <Skeleton className="h-10 w-full" />
                  <Skeleton className="h-10 w-full" />
                </div>
              ) : candidates.length === 0 ? (
                <div className="p-5">
                  <EmptyState
                    icon={Users}
                    title="No candidates found"
                    description="Try a different search or upload a resume to expand the database."
                    compact
                  />
                </div>
              ) : (
                <div className="overflow-x-auto scrollbar-thin">
                  <table className="w-full min-w-[760px] text-sm">
                    <thead>
                      <tr className="border-b bg-slate-50/80 text-left text-xs uppercase tracking-wide text-muted-foreground">
                        <th className="px-4 py-3 font-semibold">Candidate</th>
                        <th className="px-4 py-3 font-semibold">Experience</th>
                        <th className="px-4 py-3 font-semibold">Seniority</th>
                        <th className="px-4 py-3 font-semibold">Skills</th>
                        <th className="px-4 py-3 font-semibold">Education</th>
                        <th className="px-4 py-3 text-right font-semibold">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {sorted.map((c) => {
                        const edu = c.education?.[0];
                        return (
                          <tr
                            key={c.id}
                            className="border-b transition-colors last:border-0 hover:bg-slate-50/70"
                          >
                            <td className="px-4 py-3">
                              <p className="font-semibold text-slate-900">{c.name || "Unnamed"}</p>
                              <p className="text-xs text-muted-foreground">{c.job_title || "—"}</p>
                            </td>
                            <td className="px-4 py-3">{yearLabel(c.total_experience_years)}</td>
                            <td className="px-4 py-3">
                              <Badge variant="secondary">{c.seniority_level || "—"}</Badge>
                            </td>
                            <td className="max-w-[220px] px-4 py-3">
                              <div className="flex flex-wrap gap-1">
                                {(c.capability_tags ?? []).slice(0, 4).map((t) => (
                                  <Badge key={t} variant="default" className="text-[10px]">
                                    {t}
                                  </Badge>
                                ))}
                                {(c.capability_tags ?? []).length > 4 && (
                                  <Badge variant="outline" className="text-[10px]">
                                    +{(c.capability_tags ?? []).length - 4}
                                  </Badge>
                                )}
                              </div>
                            </td>
                            <td className="max-w-[200px] px-4 py-3">
                              <span className="flex items-center gap-1 truncate text-xs text-slate-600">
                                <GraduationCap className="h-3.5 w-3.5 shrink-0 text-violet-600" />
                                <span className="truncate">
                                  {[edu?.degree, edu?.field].filter(Boolean).join(" · ") || "—"}
                                </span>
                              </span>
                            </td>
                            <td className="px-4 py-3 text-right">
                              <Button variant="outline" size="sm" onClick={() => setDetailId(c.id)}>
                                <Eye className="h-3.5 w-3.5" />
                                View
                              </Button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}

              <div className="flex flex-wrap items-center justify-between gap-3 border-t px-4 py-3">
                <p className="text-xs text-muted-foreground">
                  Showing <strong className="text-slate-700">{total === 0 ? 0 : start}</strong>–
                  <strong className="text-slate-700">{total === 0 ? 0 : end}</strong> of{" "}
                  <strong className="text-slate-700">{formatNumber(total)}</strong>
                </p>
                <div className="flex items-center gap-1.5">
                  <Button variant="outline" size="sm" disabled={page === 0 || loading} onClick={() => load({ page: Math.max(0, page - 1) })}>
                    ← Prev
                  </Button>
                  <span className="px-2 text-xs font-medium text-slate-600">
                    Page {page + 1} / {pages}
                  </span>
                  <Button variant="outline" size="sm" disabled={page + 1 >= pages || loading} onClick={() => load({ page: Math.min(pages - 1, page + 1) })}>
                    Next →
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <CandidateDetailDrawer candidateId={detailId} onClose={() => setDetailId(null)} />
    </section>
  );
}