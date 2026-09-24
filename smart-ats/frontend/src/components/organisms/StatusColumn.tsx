"use client";

import React from "react";
import { CandidateCard, CandidateCardData } from "@/molecules/CandidateCard";

interface StatusColumnProps {
  title: string;
  stageKey: string;
  candidates: CandidateCardData[];
  onCandidateClick?: (candidate: CandidateCardData) => void;
  className?: string;
}

export const StatusColumn: React.FC<StatusColumnProps> = ({
  title,
  stageKey,
  candidates,
  onCandidateClick,
  className = "",
}) => {
  const isFlaggedStage = stageKey === "FLAGGED_REJECTED";

  return (
    <div
      className={`flex flex-col min-w-[280px] w-full max-w-xs rounded-2xl border p-4 backdrop-blur-xl transition-all duration-200 ${
        isFlaggedStage
          ? "bg-rose-950/20 border-rose-900/50 shadow-[0_0_15px_rgba(244,63,94,0.08)]"
          : "bg-slate-900/50 border-slate-800/80 shadow-[0_4px_24px_rgba(0,0,0,0.2)]"
      } ${className}`}
      dir="rtl"
    >
      {/* سرستون وضعیت */}
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <span
            className={`w-2.5 h-2.5 rounded-full ${
              isFlaggedStage ? "bg-rose-500 animate-pulse" : "bg-teal-400"
            }`}
          />
          <h3 className="text-sm font-bold text-slate-200">{title}</h3>
        </div>
        <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-slate-800 text-teal-300 border border-slate-700/60">
          {candidates.length}
        </span>
      </div>

      {/* لیست کارت‌های داخل ستون */}
      <div className="flex flex-col gap-3 overflow-y-auto max-h-[calc(100vh-250px)] pr-1">
        {candidates.length === 0 ? (
          <div className="p-6 text-center rounded-xl border border-dashed border-slate-800/60 text-xs text-slate-500">
            متقاضی فعالی در این مرحله نیست
          </div>
        ) : (
          candidates.map((candidate) => (
            <CandidateCard
              key={candidate.id}
              candidate={candidate}
              onClick={() => onCandidateClick?.(candidate)}
            />
          ))
        )}
      </div>
    </div>
  );
};