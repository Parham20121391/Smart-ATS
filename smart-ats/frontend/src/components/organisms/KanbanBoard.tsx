"use client";

import React from "react";
import { StatusColumn } from "./StatusColumn";
import { CandidateCardData } from "@/molecules/CandidateCard";

// وضعیت‌های مجاز و استاندارد ماشین وضعیت پروژه
export const KANBAN_STAGES = [
  { key: "REGISTERED", title: "ثبت‌نام اولیه" },
  { key: "PENDING_VERIFICATION", title: "در انتظار اعتبارسنجی" },
  { key: "SCREENING", title: "غربالگری هوشمند" },
  { key: "TECH_INTERVIEW", title: "مصاحبه فنی" },
  { key: "HR_INTERVIEW", title: "مصاحبه منابع انسانی" },
  { key: "OFFER_EXTENDED", title: "ارائه پیشنهاد" },
  { key: "HIRED", title: "استخدام نهایی" },
  { key: "FLAGGED_REJECTED", title: "رد شده / متقلب" },
];

interface KanbanBoardProps {
  candidates: CandidateCardData[];
  onCandidateClick?: (candidate: CandidateCardData) => void;
  className?: string;
}

export const KanbanBoard: React.FC<KanbanBoardProps> = ({
  candidates,
  onCandidateClick,
  className = "",
}) => {
  return (
    <div
      className={`w-full overflow-x-auto pb-6 pt-2 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent ${className}`}
      dir="rtl"
    >
      <div className="flex gap-4 min-w-max items-start">
        {KANBAN_STAGES.map((stage) => {
          const stageCandidates = candidates.filter(
            (c) => c.current_status === stage.key
          );

          return (
            <StatusColumn
              key={stage.key}
              stageKey={stage.key}
              title={stage.title}
              candidates={stageCandidates}
              onCandidateClick={onCandidateClick}
            />
          );
        })}
      </div>
    </div>
  );
};