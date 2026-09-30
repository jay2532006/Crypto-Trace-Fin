import { UserRole } from "@/types/auth";

export const ROLE_PERMISSIONS: Record<UserRole, string[]> = {
  INVESTIGATOR: [
    "cases:read",
    "cases:create",
    "trace:execute",
    "notices:read",
    "notices:draft",
    "evidence:read",
    "evidence:verify",
    "audit:read",
  ],
  SUPERVISOR: [
    "cases:read",
    "cases:create",
    "cases:assign",
    "trace:execute",
    "notices:read",
    "notices:draft",
    "notices:submit",
    "notices:approve",
    "notices:reject",
    "evidence:read",
    "evidence:verify",
    "audit:read",
    "audit:verify",
  ],
  ADMINISTRATOR: [
    "cases:read",
    "cases:create",
    "cases:assign",
    "cases:delete",
    "trace:execute",
    "notices:read",
    "notices:draft",
    "notices:submit",
    "notices:approve",
    "notices:reject",
    "evidence:read",
    "evidence:verify",
    "audit:read",
    "audit:verify",
    "system:configure",
    "diagnostics:run",
    "users:manage",
  ],
  INTEGRATION_SERVICE: [
    "cases:read",
    "cases:create",
    "trace:execute",
    "evidence:create",
    "audit:create",
  ],
};

export function hasPermission(role: UserRole | undefined, permission: string): boolean {
  if (!role) return false;
  const permissions = ROLE_PERMISSIONS[role] || [];
  return permissions.includes(permission);
}

export function canApproveNotice(role?: UserRole): boolean {
  return role === "SUPERVISOR" || role === "ADMINISTRATOR";
}
