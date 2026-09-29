import { UserSession } from "@/types/auth";

export const PRESET_USERS = [
  { id: '1', username: 'investigator1', fullName: 'Investigator', role: 'INVESTIGATOR', unit: 'Unit1' }
];

export const getCurrentSession = (): UserSession | null => {
  return null;
};

export const loginUser = async (...args: any[]): Promise<UserSession> => {
  return PRESET_USERS[0] as unknown as UserSession;
};

export const logoutUser = async () => {
  console.log("Logging out");
};
