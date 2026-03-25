/**
 * @module ProtectedRoute
 * @desc Komponen route guard yang memvalidasi autentikasi sebelum rendering.
 *       Redirect ke login jika user belum terautentikasi.
 * @author Azhar Maulana
 * @date 25 Maret 2026
 * @version 1.0
 */

import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useSelector } from 'react-redux';

/**
 * Komponen Protected Route — wrapper untuk halaman yang membutuhkan autentikasi.
 *
 * @param {object} props
 * @param {JSX.Element} [props.children] - Child component (jika digunakan sebagai wrapper langsung).
 * @param {string[]} [props.allowedRoles] - Daftar role yang diizinkan (opsional).
 * @returns {JSX.Element} Outlet atau redirect ke login.
 */
function ProtectedRoute({ children, allowedRoles }) {
  const { user, isAuthenticated } = useSelector((state) => state.auth);

  // Cek autentikasi
  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  // Cek role (jika ditentukan)
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />;
  }

  return children || <Outlet />;
}

export default ProtectedRoute;
