import { lazy, Suspense } from "react";
import { Routes, Route, Navigate } from "react-router-dom";

import MainLayout from "./layouts/MainLayout";

import HomePage from "./pages/HomePage";
import AiPage from "./pages/AiPage";
import DirectionsPage from "./pages/DirectionsPage";
import AboutPage from "./pages/AboutPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import ForbiddenPage from "./pages/ForbiddenPage";
import ProtectedRoute from "./auth/ProtectedRoute";

const ProfilePage = lazy(() => import("./pages/ProfilePage"));
const ResumePage = lazy(() => import("./pages/ResumePage"));
const InterviewPage = lazy(() => import("./pages/InterviewPage"));
const AdminUsersPage = lazy(() => import("./pages/AdminUsersPage"));
const ResourcesPage = lazy(() => import("./pages/ResourcesPage"));

function PageLoader() {
  return (
    <div className="page-wrapper">
      <div className="profile-card">
        <p className="muted">Загрузка страницы...</p>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/ai" element={<AiPage />} />
          <Route path="/directions" element={<DirectionsPage />} />
          <Route path="/resources" element={<ResourcesPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forbidden" element={<ForbiddenPage />} />

          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/interview/:id"
            element={
              <ProtectedRoute permissions={["ai_sessions:read:own"]}>
                <InterviewPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/resume"
            element={
              <ProtectedRoute permissions={["ai_sessions:create"]}>
                <ResumePage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin/users"
            element={
              <ProtectedRoute roles={["admin"]} permissions={["admin:panel"]}>
                <AdminUsersPage />
              </ProtectedRoute>
            }
          />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </Suspense>
  );
}
