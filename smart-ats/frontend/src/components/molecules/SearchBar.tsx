"use client";

import React from "react";
import { Input } from "@/atoms/Input";

interface SearchBarProps {
  searchTerm: string;
  onSearchChange: (value: string) => void;
  filterStatus?: string;
  onFilterChange?: (status: string) => void;
  className?: string;
}

const FILTER_OPTIONS = [
  { label: "همه متقاضیان", value: "ALL" },
  { label: "تایید اصالت شده", value: "VERIFIED" },
  { label: "نیازمند بررسی", value: "PENDING" },
  { label: "مشکوک به تقلب", value: "FLAGGED" },
];

export const SearchBar: React.FC<SearchBarProps> = ({
  searchTerm,
  onSearchChange,
  filterStatus = "ALL",
  onFilterChange,
  className = "",
}) => {
  return (
    <div
      className={`w-full p-4 rounded-2xl bg-slate-900/40 border border-slate-800/80 backdrop-blur-xl flex flex-col md:flex-row gap-4 items-center justify-between ${className}`}
      dir="rtl"
    >
      <div className="w-full md:w-2/3">
        <Input
          placeholder="جستجوی نام متقاضی یا مهارت کلیدی..."
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
          className="bg-slate-950/50 border-slate-800"
        />
      </div>

      <div className="flex items-center gap-2 w-full md:w-auto overflow-x-auto pb-1 md:pb-0">
        {FILTER_OPTIONS.map((opt) => {
          const isActive = filterStatus === opt.value;
          return (
            <button
              key={opt.value}
              type="button"
              onClick={() => onFilterChange?.(opt.value)}
              className={`px-3 py-1.5 text-xs font-medium rounded-xl transition-all duration-200 whitespace-nowrap border ${
                isActive
                  ? "bg-teal-500/20 text-teal-300 border-teal-500/40 shadow-[0_0_12px_rgba(20,184,166,0.2)]"
                  : "bg-slate-800/50 text-slate-400 border-slate-700/50 hover:text-slate-200 hover:bg-slate-800"
              }`}
            >
              {opt.label}
            </button>
          );
        })}
      </div>
    </div>
  );
};