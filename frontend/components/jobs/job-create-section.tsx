"use client";

import * as React from "react";
import {
  FilePlus2,
  Upload,
  RotateCcw,
  Loader2,
  CheckCircle2,
  Briefcase,
} from "lucide-react";
import { toast } from "sonner";
import { useApp } from "@/lib/app-context";
import { createJob, ApiError } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const EMPTY = {
  title: "",
  department: "",
  jobType: "",
  location: "",
  workMode: "",
  salary: "",
  minExp: "",
  maxExp: "",
  education: "",
  requiredSkills: "",
  preferredSkills: "",
  description: "",
};

type FormState = typeof EMPTY;

function buildDescription(form: FormState): string {
  const parts: string[] = [];

  if (form.department.trim()) parts.push(`### Department\n${form.department.trim()}`);
  if (form.jobType.trim()) parts.push(`### Job Type\n${form.jobType.trim()}`);
  if (form.location.trim()) parts.push(`### Location\n${form.location.trim()}`);
  if (form.workMode.trim()) parts.push(`### Work Mode\n${form.workMode.trim()}`);
  if (form.salary.trim()) parts.push(`### Compensation\n${form.salary.trim()}`);

  const minExp = parseFloat(form.minExp);
  const maxExp = parseFloat(form.maxExp);
  if (!Number.isNaN(minExp) && !Number.isNaN(maxExp)) {
    parts.push(`### Experience Required\nMinimum ${minExp} years, up to ${maxExp} years of experience required.`);
  } else if (!Number.isNaN(minExp)) {
    parts.push(`### Experience Required\nMinimum ${minExp} years of experience required.`);
  } else if (!Number.isNaN(maxExp)) {
    parts.push(`### Experience Required\nUp to ${maxExp} years of experience required.`);
  }

  if (form.education.trim()) parts.push(`### Education\n${form.education.trim()}`);

  if (form.requiredSkills.trim()) {
    parts.push(`## Required Technical Skills\n${form.requiredSkills.trim()}`);
  }
  if (form.preferredSkills.trim()) {
    parts.push(`## Preferred Skills\n${form.preferredSkills.trim()}`);
  }

  const header = parts.join("\n\n");
  const body = form.description.trim();
  if (!header) return body;
  if (!body) return header;
  return `${header}\n\n${body}`;
}

export function JobCreateSection() {
  const { refreshJobs, setSelectedJobId, scrollToSection } = useApp();
  const [form, setForm] = React.useState<FormState>(EMPTY);
  const [mode, setMode] = React.useState<"text" | "file">("text");
  const [file, setFile] = React.useState<File | null>(null);
  const [errors, setErrors] = React.useState<Record<string, string>>({});
  const [submitting, setSubmitting] = React.useState(false);
  const [created, setCreated] = React.useState<{ title: string; id: number; mandatory: string } | null>(null);

  const set = (key: keyof FormState) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setForm((f) => ({ ...f, [key]: e.target.value }));
    setErrors((err) => ({ ...err, [key]: "" }));
  };

  const reset = () => {
    setForm(EMPTY);
    setFile(null);
    setErrors({});
    setCreated(null);
  };

  const validate = (): boolean => {
    const errs: Record<string, string> = {};
    if (!form.title.trim()) errs.title = "Job title is required.";
    if (mode === "text" && !form.description.trim()) {
      errs.description = "Paste the full job description or switch to file upload.";
    } else if (mode === "text" && form.description.trim().length < 60) {
      errs.description = "The job description looks too short to be useful (min ~60 characters).";
    }
    if (mode === "file" && !file) errs.file = "Select a JD file (.pdf, .docx, .txt or .md).";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting || !validate()) return;

    setSubmitting(true);
    setCreated(null);
    try {
      const job = await createJob({
        title: form.title.trim(),
        ...(mode === "file" && file ? { file } : { description: buildDescription(form) }),
      });
      toast.success(`Job "${job.title}" created.`, {
        description: `ID ${job.id} ready for ranking.`,
      });
      setCreated({ title: job.title, id: job.id, mandatory: job.is_mandatory_requirements || "—" });
      reset();
      await refreshJobs(job.id);
      setSelectedJobId(job.id);
      scrollToSection("rank");
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "Failed to create the job.";
      toast.error(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const fieldCls = "rounded-md border border-input bg-background";
  const inputWrapCls = "space-y-1.5";

  return (
    <section id="create-job" className="section-anchor">
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
          <FilePlus2 className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-lg font-bold tracking-tight text-slate-900">Create Job Description</h2>
          <p className="text-xs text-muted-foreground">
            Add a position and build a structured job description for AI matching
          </p>
        </div>
      </div>

      <Card>
        <CardContent className="p-5 sm:p-6">
          <form onSubmit={onSubmit} className="space-y-5" noValidate>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <div className={cn(inputWrapCls, "sm:col-span-2 lg:col-span-3")}>
                <Label htmlFor="jd-title">
                  Job title <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="jd-title"
                  placeholder="e.g. Senior Machine Learning Engineer"
                  value={form.title}
                  onChange={set("title")}
                  aria-invalid={!!errors.title}
                />
                {errors.title && <p className="text-xs text-destructive">{errors.title}</p>}
              </div>

              <div className={inputWrapCls}>
                <Label htmlFor="jd-dept">Department</Label>
                <Input id="jd-dept" placeholder="e.g. Engineering, Product, Data Science" value={form.department} onChange={set("department")} />
              </div>
              <div className={inputWrapCls}>
                <Label htmlFor="jd-type">Job type</Label>
                <Select id="jd-type" value={form.jobType} onChange={set("jobType")}>
                  <option value="">Select type…</option>
                  <option>Full-time</option>
                  <option>Part-time</option>
                  <option>Contract</option>
                  <option>Internship</option>
                  <option>Freelance</option>
                </Select>
              </div>
              <div className={inputWrapCls}>
                <Label htmlFor="jd-location">Location</Label>
                <Input id="jd-location" placeholder="e.g. Bengaluru, Hyderabad or Remote" value={form.location} onChange={set("location")} />
              </div>

              <div className={inputWrapCls}>
                <Label htmlFor="jd-mode">Work mode</Label>
                <Select id="jd-mode" value={form.workMode} onChange={set("workMode")}>
                  <option value="">Select mode…</option>
                  <option>On-site</option>
                  <option>Hybrid</option>
                  <option>Remote</option>
                </Select>
              </div>
              <div className={inputWrapCls}>
                <Label htmlFor="jd-salary">Salary range</Label>
                <Input id="jd-salary" placeholder="e.g. ₹25-40 LPA" value={form.salary} onChange={set("salary")} />
              </div>
              <div className={inputWrapCls}>
                <Label htmlFor="jd-min-exp">Minimum experience (years)</Label>
                <Input id="jd-min-exp" type="number" min={0} max={40} placeholder="e.g. 3" value={form.minExp} onChange={set("minExp")} />
              </div>
              <div className={inputWrapCls}>
                <Label htmlFor="jd-max-exp">Maximum experience (years)</Label>
                <Input id="jd-max-exp" type="number" min={0} max={40} placeholder="e.g. 8" value={form.maxExp} onChange={set("maxExp")} />
              </div>
              <div className={inputWrapCls}>
                <Label htmlFor="jd-edu">Education requirement</Label>
                <Input id="jd-edu" placeholder="e.g. Bachelor's degree in Computer Science" value={form.education} onChange={set("education")} />
              </div>

              <div className={inputWrapCls}>
                <Label htmlFor="jd-required">Required skills <span className="font-normal text-muted-foreground">(comma separated)</span></Label>
                <Input id="jd-required" placeholder="Python, PyTorch, FastAPI, PostgreSQL, Docker" value={form.requiredSkills} onChange={set("requiredSkills")} />
              </div>
              <div className={inputWrapCls}>
                <Label htmlFor="jd-preferred">Preferred skills <span className="font-normal text-muted-foreground">(comma separated)</span></Label>
                <Input id="jd-preferred" placeholder="Kubernetes, AWS, Airflow, LangChain" value={form.preferredSkills} onChange={set("preferredSkills")} />
              </div>
              <div className={cn(inputWrapCls, "sm:col-span-2")}>
                <Label>Job description source</Label>
                <div className="inline-flex rounded-md border bg-secondary/60 p-0.5">
                  {(["text", "file"] as const).map((m) => (
                    <button
                      key={m}
                      type="button"
                      onClick={() => setMode(m)}
                      className={cn(
                        "rounded px-3 py-1 text-xs font-medium transition-colors",
                        mode === m ? "bg-background text-slate-900 shadow-sm" : "text-muted-foreground",
                      )}
                    >
                      {m === "text" ? "Paste text" : "Upload file"}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {mode === "file" ? (
              <div className="space-y-1.5">
                <Label htmlFor="jd-file">JD document</Label>
                <label
                  htmlFor="jd-file"
                  className="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed px-4 py-8 text-center transition-colors hover:border-primary/50 hover:bg-primary/5"
                >
                  <Upload className="h-6 w-6 text-muted-foreground" />
                  <span className="text-sm font-medium text-slate-700">
                    {file ? file.name : "Choose a JD file (.pdf, .docx, .txt, .md)"}
                  </span>
                  {file && (
                    <span className="text-xs text-muted-foreground">
                      {(file.size / 1024).toFixed(1)} KB
                    </span>
                  )}
                  <input
                    id="jd-file"
                    type="file"
                    accept=".pdf,.docx,.txt,.md"
                    className="sr-only"
                    onChange={(e) => {
                      setFile(e.target.files?.[0] ?? null);
                      setErrors((err) => ({ ...err, file: "" }));
                    }}
                  />
                </label>
                {errors.file && <p className="text-xs text-destructive">{errors.file}</p>}
              </div>
            ) : (
              <div className="space-y-1.5">
                <Label htmlFor="jd-description">
                  Full job description <span className="text-destructive">*</span>
                  <span className="ml-2 font-normal text-muted-foreground">
                    Pasted text is never truncated or altered.
                  </span>
                </Label>
                <Textarea
                  id="jd-description"
                  rows={14}
                  placeholder={
                    "Paste the complete job description here…\n\nAI/ML Engineer\nRequired Technical Skills\nPreferred Skills\nEducation\nResponsibilities\nWhat We Offer"
                  }
                  value={form.description}
                  onChange={set("description")}
                  className="min-h-[280px] font-mono text-[13px] leading-relaxed"
                  aria-invalid={!!errors.description}
                />
                {errors.description && <p className="text-xs text-destructive">{errors.description}</p>}
              </div>
            )}

            <div className="rounded-lg border bg-slate-50/70 p-3 text-xs text-muted-foreground">
              <strong className="text-slate-600">Note:</strong> the optional detail fields are merged into a
              structured section at the top of the job description so the parser can extract required skills,
              experience range and education correctly. Your pasted JD text stays intact.
            </div>

            {created && (
              <div className="flex items-start gap-2.5 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800 animate-fade-in">
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0" />
                <div>
                  <p className="font-semibold">
                    Job created — {created.title} (ID: {created.id})
                  </p>
                  <p className="mt-0.5 text-xs text-emerald-700">
                    Mandatory skills: {created.mandatory}. Scrolling you to the ranking section…
                  </p>
                </div>
              </div>
            )}

            <div className="flex flex-wrap items-center justify-end gap-2 border-t pt-4">
              <Button type="button" variant="outline" onClick={reset} disabled={submitting}>
                <RotateCcw className="h-4 w-4" />
                Reset form
              </Button>
              <Button type="submit" disabled={submitting}>
                {submitting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Creating job…
                  </>
                ) : (
                  <>
                    <Briefcase className="h-4 w-4" />
                    Create Job &amp; Rank
                  </>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
      <div className="mt-3 flex items-center justify-end gap-2">
        <Badge variant="secondary">Parsed sections: required skills · preferred skills · experience · education</Badge>
      </div>
    </section>
  );
}