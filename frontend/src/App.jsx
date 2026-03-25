/**
 * @module App
 * @desc Konfigurasi React Router dengan protected routes dan role-based rendering.
 *       Menggunakan AnimatePresence dari Framer Motion untuk page transitions.
 * @author Azhar Maulana
 * @date 25 Maret 2026
 * @version 1.0
 */

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { useSelector } from 'react-redux';

import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import SessionPage from './pages/SessionPage';
import StudentsPage from './pages/StudentsPage';
import FocusModePage from './pages/FocusModePage';
import ProtectedRoute from './components/ProtectedRoute';
import Sidebar from './components/Sidebar';

/**
 * Komponen utama aplikasi dengan routing dan layout.
 * @returns {JSX.Element} Aplikasi Zonara.
 */
function App() {
  const { user } = useSelector((state) => state.auth);

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar hanya muncul jika user sudah login dan bukan di Focus Mode */}
      {user && (
        <Sidebar />
      )}

      {/* Main Content Area */}
      <main className={`flex-1 overflow-y-auto ${user ? 'ml-0' : ''}`}>
        <AnimatePresence mode="wait">
          <Routes>
            {/* Public Routes */}
            <Route
              path="/login"
              element={user ? <Navigate to="/dashboard" replace /> : <LoginPage />}
            />

            {/* Protected Routes */}
            <Route element={<ProtectedRoute />}>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/sessions" element={<SessionPage />} />
              <Route path="/students" element={<StudentsPage />} />
            </Route>

            {/* Focus Mode (full-screen tanpa sidebar) */}
            <Route
              path="/focus/:sessionId"
              element={
                <ProtectedRoute>
                  <FocusModePage />
                </ProtectedRoute>
              }
            />

            {/* Default redirect */}
            <Route path="*" element={<Navigate to={user ? "/dashboard" : "/login"} replace />} />
          </Routes>
        </AnimatePresence>
      </main>
    </div>
  );
}

export default App;
