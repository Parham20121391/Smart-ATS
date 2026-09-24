import React from "react";

interface SkillBadgeProps {
  skill: string;
  variant?: "default" | "verified" | "unverified";
  className?: string;
}

export const SkillBadge: React.FC<SkillBadgeProps> = ({
  skill,
  variant = "default",
  className = "",
}) => {
  const variantStyles = {
    default:
      "bg-slate-800/80 text-slate-300 border-slate-700/60 hover:border-slate-600",
    verified:
      "bg-teal-500/10 text-teal-300 border-teal-500/30 hover:border-teal-500/50 shadow-[0_0_10px_rgba(20,184,166,0.15)]",
    unverified:
      "bg-amber-500/10 text-amber-300 border-amber-500/30 hover:border-amber-500/50",
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium border backdrop-blur-md transition-all duration-150 select-none ${variantStyles[variant]} ${className}`}
    >
      {variant === "verified" && (
        <span className="w-1.5 h-1.5 rounded-full bg-teal-400 animate-pulse" />
      )}
      <span>{skill}</span>
    </span>
  );
};