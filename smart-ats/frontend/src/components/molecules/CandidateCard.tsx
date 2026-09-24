import React from "react";
import { SkillBadge } from "@/atoms/SkillBadge";

export interface CandidateCardData {
  id: number;
  first_name: string;
  last_name: string;
  current_status: string;
  integrity_flag: boolean;
  skills?: string[];
  avatar_url?: string;
}

interface CandidateCardProps {
  candidate: CandidateCardData;
  onClick?: () => void;
  className?: string;
}

export const CandidateCard: React.FC<CandidateCardProps> = ({
  candidate,
  onClick,
  className = "",
}) => {
  const { first_name, last_name, integrity_flag, skills = [], avatar_url } = candidate;

  // استخراج حروف اول نام برای آواتار پیش‌فرض
  const initials = `${first_name?.[0] || ""}${last_name?.[0] || ""}`.toUpperCase();

  return (
    <div
      onClick={onClick}
      className={`group relative p-4 rounded-xl transition-all duration-200 cursor-pointer ${
        integrity_flag
          ? "glass-cyber-card"
          : "bg-rose-950/10 border border-rose-900/40 hover:border-rose-500/40"
      } ${className}`}
      dir="rtl"
    >
      <div className="flex items-center gap-3 mb-3">
        {avatar_url ? (
          <img
            src={avatar_url}
            alt={`${first_name} ${last_name}`}
            className="w-10 h-10 rounded-full object-cover border border-slate-700"
          />
        ) : (
          <div className="w-10 h-10 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-bold text-teal-300">
            {initials || "کارجو"}
          </div>
        )}

        <div className="flex flex-col text-right">
          <span className="text-sm font-semibold text-slate-100 group-hover:text-teal-300 transition-colors">
            {first_name} {last_name}
          </span>
          <span
            className={`text-[11px] font-medium mt-0.5 ${
              integrity_flag ? "text-emerald-400" : "text-rose-400"
            }`}
          >
            {integrity_flag ? "احراز هویت شده" : "مشکوک به جعل"}
          </span>
        </div>
      </div>

      {skills.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-2">
          {skills.slice(0, 4).map((skill, index) => (
            <SkillBadge
              key={index}
              skill={skill}
              variant={integrity_flag ? "verified" : "default"}
            />
          ))}
          {skills.length > 4 && (
            <span className="text-[10px] text-slate-500 self-center">
              +{skills.length - 4}
            </span>
          )}
        </div>
      )}
    </div>
  );
};