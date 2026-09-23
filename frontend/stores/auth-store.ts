import { create } from "zustand";
import { UserSession, UserRole } from "@/types/auth";
import { getCurrentSession, logoutUser } from "@/lib/auth";

export interface AuthUser {
  username: string;
  name: string;
  role: UserRole;
  unit: string;
}

interface AuthState {
  session: UserSession | null;
  user: AuthUser | null;
  isLoading: boolean;
  setSession: (session: UserSession | null) => void;
  logout: () => void;
  initialize: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  session: null,
  user: null,
  isLoading: true,
  setSession: (session) =>
    set({
      session,
      user: session
        ? {
            username: session.username,
            name: session.fullName,
            role: session.role,
            unit: session.unit,
          }
        : null,
      isLoading: false,
    }),
  logout: () => {
    logoutUser();
    set({ session: null, user: null });
  },
  initialize: () => {
    const s = getCurrentSession();
    set({
      session: s,
      user: s
        ? {
            username: s.username,
            name: s.fullName,
            role: s.role,
            unit: s.unit,
          }
        : null,
      isLoading: false,
    });
  },
}));
