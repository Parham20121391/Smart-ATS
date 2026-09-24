import React from "react";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  helperText,
  id,
  className = "",
  disabled,
  ...props
}) => {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, "-") : undefined);

  return (
    <div className="w-full flex flex-col gap-1.5 text-right" dir="rtl">
      {label && (
        <label
          htmlFor={inputId}
          className="text-xs font-medium text-slate-300 select-none"
        >
          {label}
        </label>
      )}

      <input
        id={inputId}
        disabled={disabled}
        className={`w-full px-4 py-2.5 rounded-xl bg-slate-900/60 border text-slate-100 placeholder-slate-500 text-sm backdrop-blur-md outline-none transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed ${
          error
            ? "border-rose-500/80 focus:border-rose-400 focus:ring-1 focus:ring-rose-500/50 shadow-[0_0_10px_rgba(244,63,94,0.15)]"
            : "border-slate-800 focus:border-teal-500/50 focus:ring-1 focus:ring-teal-500/30 focus:shadow-[0_0_12px_rgba(20,184,166,0.15)]"
        } ${className}`}
        {...props}
      />

      {error ? (
        <span className="text-xs text-rose-400 font-normal animate-fadeIn">
          {error}
        </span>
      ) : helperText ? (
        <span className="text-xs text-slate-400">{helperText}</span>
      ) : null}
    </div>
  );
};