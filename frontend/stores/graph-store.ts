import { create } from "zustand";
import { HopNode } from "@/types/domain";

interface GraphState {
  selectedNode: HopNode | null;
  hoveredNode: HopNode | null;
  highlightedPath: string[];
  filterMinAmount: number;
  hideMixers: boolean;
  setSelectedNode: (node: HopNode | null) => void;
  setHoveredNode: (node: HopNode | null) => void;
  setHighlightedPath: (path: string[]) => void;
  setFilterMinAmount: (amt: number) => void;
  setHideMixers: (hide: boolean) => void;
  resetFilters: () => void;
}

export const useGraphStore = create<GraphState>((set) => ({
  selectedNode: null,
  hoveredNode: null,
  highlightedPath: [],
  filterMinAmount: 0,
  hideMixers: false,
  setSelectedNode: (selectedNode) => set({ selectedNode }),
  setHoveredNode: (hoveredNode) => set({ hoveredNode }),
  setHighlightedPath: (highlightedPath) => set({ highlightedPath }),
  setFilterMinAmount: (filterMinAmount) => set({ filterMinAmount }),
  setHideMixers: (hideMixers) => set({ hideMixers }),
  resetFilters: () => set({ selectedNode: null, hoveredNode: null, highlightedPath: [], filterMinAmount: 0, hideMixers: false }),
}));
