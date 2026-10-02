// smart-ats/frontend/src/store/useKanbanStore.ts
import { create } from 'zustand';
import axios, { AxiosError } from 'axios';

// اینترفیس کاندیدا (تسک ۲۶)
export interface Candidate {
  id: number;
  first_name: string;
  last_name: string;
  current_status: string;
  integrity_flag: boolean;
}

// اینترفیس استیت و اکشن‌های استور (تسک ۲۷)
export interface KanbanState {
  candidates: Candidate[];
  fetchCandidates: () => Promise<void>;
  moveCandidate: (candidateId: number, nextState: string) => Promise<void>;
  updateCandidateStateInStore: (candidateId: number, nextState: string) => void;
}

// مقداردهی اولیه و هوک استور (تسک ۲۴ و ۲۸)
export const useKanbanStore = create<KanbanState>((set, get) => ({
  candidates: [],

  fetchCandidates: async () => {
    try {
      const response = await axios.get('/api/v1/applications');
      set({ candidates: response.data });
    } catch (error) {
      console.error("خطا در واکشی کاندیداها:", error);
    }
  },

  moveCandidate: async (candidateId: number, nextState: string) => {
    try {
      await axios.patch(`/api/v1/applications/${candidateId}/status`, {
        current_status: nextState,
      });
      await get().fetchCandidates();
    } catch (error) {
      const err = error as AxiosError<{ detail?: string }>;
      alert(`خطای ماشین وضعیت: ${err.response?.data?.detail || "انتقال غیرمجاز"}`);
    }
  },

  updateCandidateStateInStore: (candidateId: number, nextState: string) => {
    const currentCandidates = get().candidates;
    const updated = currentCandidates.map((c) =>
      c.id === candidateId ? { ...c, current_status: nextState } : c
    );
    set({ candidates: updated });
  },
}));