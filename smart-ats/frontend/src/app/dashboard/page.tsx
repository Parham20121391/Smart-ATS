// smart-ats/frontend/src/app/dashboard/page.tsx
"use client";

import React, { useEffect } from "react";
import { useKanbanStore } from "@/store/useKanbanStore";
import { KanbanBoard } from "@/organisms/KanbanBoard";

export default function EmployerDashboardPage() {
  const { candidates, fetchCandidates, moveCandidate } = useKanbanStore();

  useEffect(() => {
    fetchCandidates();
  }, [fetchCandidates]);

  return (
    <div className="w-full flex flex-col gap-6" dir="rtl">
      <header className="border-b border-slate-800 pb-4">
        <h1 className="text-3xl font-bold text-teal-400">داشبورد مدیریت متقاضیان (Kanban)</h1>
        <p className="text-sm text-slate-400 mt-1">
          رندر کلاینت‌ساید با سیستم مدیریت وضعیت سریع Zustand و انتقال هوشمند درگ اند دراپ
        </p>
      </header>

      <KanbanBoard
        candidates={candidates}
        onDropCandidate={(candidateId, nextState) => {
          moveCandidate(candidateId, nextState);
        }}
      />
    </div>
  );
}