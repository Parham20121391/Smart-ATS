"use client";

import { useEffect, useState } from "react";

interface Application {
  id: number;
  first_name: string;
  last_name: string;
  current_status: string;
  integrity_flag: boolean;
}

// وضعیت‌های مجاز چرخه استخدام در بورد کانبان
const KANBAN_STAGES = [
  "REGISTERED",
  "PENDING_VERIFICATION",
  "SCREENING",
  "TECH_INTERVIEW",
  "HR_INTERVIEW",
  "OFFER_EXTENDED",
];

export default function EmployerKanbanDashboard() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // لود سمت کلاینت داده‌های متقاضیان (CSR)
    const fetchApplications = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/v1/applications");
        if (res.ok) {
          const data = await res.json();
          setApplications(data);
        }
      } catch (err) {
        console.error("خطا در واکشی اطلاعات کارفرمایان:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchApplications();
  }, []);

  return (
    <div className="w-full min-h-[80vh] flex flex-col gap-6">
      <header className="border-b border-slate-800 pb-4">
        <h1 className="text-3xl font-bold text-teal-400">داشبورد مدیریت متقاضیان (Kanban)</h1>
        <p className="text-sm text-slate-400 mt-1">
          رندر کلاینت‌ساید (CSR) جهت مدیریت بلادرنگ وضعیت کاندیداها
        </p>
      </header>

      {loading ? (
        <div className="text-slate-400 animate-pulse">در حال بارگذاری وضعیت‌ها...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          {KANBAN_STAGES.map((stage) => {
            const stageApps = applications.filter((app) => app.current_status === stage);
            return (
              <div
                key={stage}
                className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3 flex flex-col gap-3 min-h-[450px]"
              >
                <div className="flex justify-between items-center pb-2 border-b border-slate-800">
                  <span className="text-xs font-semibold text-slate-300">{stage}</span>
                  <span className="text-xs bg-slate-800 px-2 py-0.5 rounded text-teal-400">
                    {stageApps.length}
                  </span>
                </div>

                <div className="flex flex-col gap-2">
                  {stageApps.map((app) => (
                    <div
                      key={app.id}
                      className="p-3 bg-slate-800/80 rounded-lg border border-slate-700/50 text-sm shadow cursor-pointer hover:border-teal-500/40 transition"
                    >
                      <p className="font-medium text-slate-200">
                        {app.first_name} {app.last_name}
                      </p>
                      <div className="mt-2 flex items-center justify-between text-xs">
                        <span
                          className={`px-1.5 py-0.5 rounded ${
                            app.integrity_flag
                              ? "bg-emerald-500/10 text-emerald-400"
                              : "bg-rose-500/10 text-rose-400"
                          }`}
                        >
                          {app.integrity_flag ? "تایید اصالت" : "مشکوک"}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}