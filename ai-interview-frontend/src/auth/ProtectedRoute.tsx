import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "./AuthContext";

type Props = {
  children: ReactNode;
  roles?: string[];
  permissions?: string[];
};

export function ProtectedRoute({ children, roles, permissions }: Props) {
  const { isAuth, loading, hasRole, hasPermission } = useAuth();

  if (loading) return <div style={{ padding: 24 }}>Загрузка...</div>;
  if (!isAuth) return <Navigate to="/login" replace />;

  if (roles?.length && !hasRole(...roles)) {
    return <Navigate to="/forbidden" replace />;
  }

  if (permissions?.length && !permissions.every((permission) => hasPermission(permission))) {
    return <Navigate to="/forbidden" replace />;
  }

  return <>{children}</>;
}

export default ProtectedRoute;
