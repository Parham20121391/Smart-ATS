"use client";

import React, { useState, useRef } from "react";

interface ResumeUploadProps {
  onFileSelect?: (file: File | null) => void;
  error?: string;
  className?: string;
}

export const ResumeUpload: React.FC<ResumeUploadProps> = ({
  onFileSelect,
  error,
  className = "",
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    setSelectedFile(file);
    if (onFileSelect) {
      onFileSelect(file);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    if (onFileSelect) {
      onFileSelect(null);
    }
  };

  return (
    <div className={`w-full flex flex-col gap-2 text-right ${className}`} dir="rtl">
      <label className="text-xs font-medium text-slate-300 select-none">
        آپلود رزومه کارجو (فقط فرمت PDF)
      </label>

      <div
        onClick={() => fileInputRef.current?.click()}
        className={`w-full p-4 rounded-xl border border-dashed flex flex-col items-center justify-center gap-2 cursor-pointer transition-all duration-200 backdrop-blur-md ${
          error
            ? "border-rose-500/80 bg-rose-500/5 hover:border-rose-400"
            : "border-slate-700 bg-slate-900/40 hover:border-teal-500/50 hover:bg-slate-900/60"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          className="hidden"
          onChange={handleFileChange}
        />

        <svg
          className="w-8 h-8 text-teal-400/80 mb-1"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.5"
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>

        {selectedFile ? (
          <div className="flex items-center gap-2 text-sm text-teal-300">
            <span>{selectedFile.name}</span>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                handleClear();
              }}
              className="text-xs text-rose-400 hover:text-rose-300 px-1 py-0.5 rounded bg-rose-500/10 border border-rose-500/20"
            >
              حذف
            </button>
          </div>
        ) : (
          <>
            <span className="text-sm text-slate-300">
              کلیک کنید یا فایل رزومه را اینجا بکشید و رها کنید
            </span>
            <span className="text-xs text-slate-500">حداکثر حجم مجاز: ۵ مگابایت</span>
          </>
        )}
      </div>

      {error && <span className="text-xs text-rose-400">{error}</span>}
    </div>
  );
};