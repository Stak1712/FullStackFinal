export type Role = "guest" | "user" | "manager" | "admin";

export type User = {
  id?: string | number;
  email?: string;
  name?: string;
  first_name?: string;
  last_name?: string;
  role?: Role | string;
  permissions?: string[];
};

export function getDisplayName(user: User | null | undefined): string {
  const fullName = [user?.first_name, user?.last_name].filter(Boolean).join(" ").trim();
  return user?.name?.trim() || fullName || user?.email || "Пользователь";
}

export function getRoleLabel(role?: string): string {
  switch (role) {
    case "admin":
      return "Администратор";
    case "manager":
      return "Менеджер";
    case "user":
      return "Пользователь";
    case "guest":
      return "Гость";
    default:
      return role || "Неизвестно";
  }
}

export function hasPermission(user: User | null | undefined, permission: string): boolean {
  return Boolean(user?.permissions?.includes(permission));
}

export function hasRole(user: User | null | undefined, roles: string[]): boolean {
  return Boolean(user?.role && roles.includes(user.role));
}
