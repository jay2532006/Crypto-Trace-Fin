export type UserRole =
  | "INVESTIGATOR"
  | "SUPERVISOR"
  | "ADMINISTRATOR"
  | "INTEGRATION_SERVICE";

export interface UserSession {
  username: string;
  fullName: string;
  role: UserRole;
  unit: string;
  token?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  role: UserRole;
  username: string;
  unit: string;
}
