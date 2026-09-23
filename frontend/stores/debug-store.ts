import { create } from "zustand";
import { LogEntry, logger } from "@/lib/logger";

interface DebugState {
  isOpen: boolean;
  isDrawerOpen: boolean;
  activeTab: "logs" | "network" | "telemetry";
  logs: LogEntry[];
  toggleOpen: () => void;
  toggleDrawer: () => void;
  setOpen: (open: boolean) => void;
  setActiveTab: (tab: "logs" | "network" | "telemetry") => void;
  refreshLogs: () => void;
  clearLogs: () => void;
}

export const useDebugStore = create<DebugState>((set) => ({
  isOpen: false,
  isDrawerOpen: false,
  activeTab: "logs",
  logs: [],
  toggleOpen: () => set((state) => ({ isOpen: !state.isOpen, isDrawerOpen: !state.isOpen, logs: logger.getRecentLogs() })),
  toggleDrawer: () => set((state) => ({ isOpen: !state.isOpen, isDrawerOpen: !state.isOpen, logs: logger.getRecentLogs() })),
  setOpen: (isOpen) => set({ isOpen, isDrawerOpen: isOpen }),
  setActiveTab: (activeTab) => set({ activeTab }),
  refreshLogs: () => set({ logs: logger.getRecentLogs() }),
  clearLogs: () => {
    logger.clearLogs();
    set({ logs: [] });
  },
}));
