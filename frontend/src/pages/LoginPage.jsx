/**
 * @module LoginPage
 * @desc Halaman login dengan form validasi dan animasi glassmorphism.
 * @author Azhar Maulana
 * @date 25 Maret 2026
 * @version 1.0
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

import { useLoginMutation } from '../store/apiSlice';
import { setCredentials } from '../store/authSlice';

/**
 * Komponen halaman login dengan form validasi.
 * @returns {JSX.Element} Halaman Login.
 */
function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [login, { isLoading }] = useLoginMutation();
  const dispatch = useDispatch();
  const navigate = useNavigate();

  /**
   * Handler submit form login.
   * @param {Event} e - Form submit event.
   */
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validasi input
    if (!username.trim() || !password.trim()) {
      toast.error('Username dan password wajib diisi.');
      return;
    }

    try {
      const result = await login({ username, password }).unwrap();

      dispatch(setCredentials({
        user: result.data.user,
        accessToken: result.data.access_token,
        refreshToken: result.data.refresh_token,
      }));

      toast.success(result.message || 'Login berhasil!');
      navigate('/dashboard');
    } catch (err) {
      const message = err?.data?.detail || 'Login gagal. Periksa username dan password.';
      toast.error(message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-900 px-4">
      {/* Background gradient */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-zona-blue-500/20 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-zona-green-500/20 rounded-full blur-3xl" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 w-full max-w-md"
      >
        {/* Logo & Title */}
        <div className="text-center mb-8">
          <motion.h1
            className="text-4xl font-display font-bold gradient-text mb-2"
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2 }}
          >
            Zonara
          </motion.h1>
          <p className="text-surface-200/60 text-sm">
            Character Analytics — Phygital Early Warning System
          </p>
        </div>

        {/* Login Card */}
        <div className="glass-card p-8">
          <h2 className="text-xl font-semibold text-white mb-6">Masuk ke Akun</h2>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Username */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-surface-200 mb-2">
                Username
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="input-field"
                placeholder="Masukkan username"
                autoComplete="username"
                disabled={isLoading}
              />
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-surface-200 mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input-field"
                placeholder="Masukkan password"
                autoComplete="current-password"
                disabled={isLoading}
              />
            </div>

            {/* Submit */}
            <motion.button
              type="submit"
              className="btn-primary w-full"
              disabled={isLoading}
              whileTap={{ scale: 0.97 }}
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Memproses...
                </span>
              ) : (
                'Masuk'
              )}
            </motion.button>
          </form>

          {/* Demo credentials */}
          <div className="mt-6 p-3 bg-surface-700/30 rounded-lg border border-surface-600/30">
            <p className="text-xs text-surface-200/50 text-center">
              Demo: <span className="text-zona-blue-400">admin_zonara</span> / <span className="text-zona-blue-400">admin123</span>
            </p>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-xs text-surface-200/30 mt-6">
          © 2026 Zonara Character Analytics — Azhar Maulana
        </p>
      </motion.div>
    </div>
  );
}

export default LoginPage;
