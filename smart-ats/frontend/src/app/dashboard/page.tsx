// smart-ats/frontend/src/app/dashboard/page.tsx
"use client";

import React, { useEffect } from "react";
import { useKanbanStore } from "@/store/useKanbanStore";
import { KanbanBoard } from "@/organisms/KanbanBoard";

export default function EmployerDashboardPage() {
  const {
    candidates,
    fetchCandidates,
    moveCandidate,
    updateCandidateStateInStore,
  } = useKanbanStore();

  useEffect(() => {
    // واکشی اولیه کاندیداها
    fetchCandidates();

    // تسک ۴۲: برقراری اتصال زنده وب‌سوکت با سرور FastAPI
    const socketUrl =
      process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/api/v1/ws/kanban";
    const socket = new WebSocket(socketUrl);

    socket.onopen = () => {
      console.log("اتصال بلادرنگ بورد کانبان برقرار شد (WebSocket Connected)");
    };

    // تسک ۴۱: شنود پیام‌ها و اعمال آنی روی استور بدون رفرش صفحه
    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (
          payload.event === "CANDIDATE_STATUS_UPDATED" &&
          payload.data
        ) {
          const { candidate_id, current_status } = payload.data;
          updateCandidateStateInStore(candidate_id, current_status);
        }
      } catch (err) {
        console.error("خطا در پردازش پیام وب‌سوکت:", err);
      }
    };

    socket.onerror = (error) => {
      console.error("خطای اتصال وب‌سوکت:", error);
    };

    socket.onclose = () => {
      console.log("اتصال وب‌سوکت بسته شد");
    };

    // پاکسازی اتصال در هنگام خروج از کامپوننت
    return () => {
      socket.close();
    };
  }, [fetchCandidates, updateCandidateStateInStore]);

  return (
    <div className="w-full flex flex-col gap-6" dir="rtl">
      <header className="border-b border-slate-800 pb-4">
        <h1 className="text-3xl font-bold text-teal-400">
          داشبورد مدیریت متقاضیان (Kanban)
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          همگام‌سازی بلادرنگ وضعیت کارجویان از طریق WebSocket و مدیریت وضعیت Zustand
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