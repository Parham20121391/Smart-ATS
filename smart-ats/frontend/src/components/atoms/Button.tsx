import React from "react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger" | "ghost";
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = "primary",
  isLoading = false,
  disabled,
  className = "",
  ...props
}) => {
  const baseStyles =
    "relative inline-flex items-center justify-center px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 backdrop-blur-md disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none";

  const variantStyles = {
    primary:
      "bg-teal-500/20 text-teal-300 border border-teal-500/30 hover:bg-teal-500/30 hover:shadow-[0_0_15px_rgba(20,184,166,0.3)]",
    secondary:
      "bg-slate-800/60 text-slate-200 border border-slate-700/60 hover:bg-slate-700/60",
    danger:
      "bg-rose-500/20 text-rose-300 border border-rose-500/30 hover:bg-rose-500/30 hover:shadow-[0_0_15px_rgba(244,63,94,0.3)]",
    ghost:
      "bg-transparent text-slate-400 hover:text-slate-100 hover:bg-slate-800/40",
  };

  return (
    <button
      disabled={disabled || isLoading}
      className={`${baseStyles} ${variantStyles[variant]} ${className}`}
      {...props}
    >
      {isLoading ? (
        <span className="flex items-center gap-2">
          <svg
            className="animate-spin h-4 w-4 text-current"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8v8H4z"
            ></path>
          </svg>
          <span>در حال پردازش...</span>
        </span>
      ) : (
        children
      )}
    </button>
  );
};