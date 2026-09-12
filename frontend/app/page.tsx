"use client";

import * as React from "react";
import { useApp } from "@/lib/app-context";
import { SECTION_IDS } from "@/lib/constants";
import { Sidebar, MobileNav } from "@/components/layout/sidebar";
import { AppHeader } from "@/components/layout/app-header";
import { DashboardOverview } from "@/components/dashboard/dashboard-overview";
import { JobCreateSection } from "@/components/jobs/job-create-section";
import { RankSection } from "@/components/ranking/rank-section";
import { RankingResults } from "@/components/ranking/ranking-results";
import { CandidateDatabase } from "@/components/candidates/candidate-database";

export default function Page() {
  const { setActiveSection } = useApp();
  const [mobileNavOpen, setMobileNavOpen] = React.useState(false);

  React.useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) setActiveSection(entry.target.id);
        }
      },
      { rootMargin: "-25% 0px -65% 0px", threshold: 0 },
    );
    const eles = SECTION_IDS.map((id) => document.getElementById(id)).filter(
      (el): el is HTMLElement => el != null,
    );
    eles.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, [setActiveSection]);

  return (
    <div className="min-h-screen">
      <Sidebar />
      <MobileNav open={mobileNavOpen} onClose={() => setMobileNavOpen(false)} />
      <div className="lg:pl-64">
        <AppHeader onMenu={() => setMobileNavOpen(true)} />
        <main className="mx-auto max-w-6xl space-y-10 px-4 py-8 sm:px-6 lg:px-8">
          <DashboardOverview />
          <JobCreateSection />
          <RankSection />
          <RankingResults />
          <CandidateDatabase />
        </main>
      </div>
    </div>
  );
}