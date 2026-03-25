/**
 * @module Helpers
 * @desc Fungsi utilitas: token storage, date formatting, score calculation.
 * @author Azhar Maulana
 * @date 25 Maret 2026
 * @version 1.0
 */

const TOKEN_KEY = 'zonara_access_token';
const REFRESH_KEY = 'zonara_refresh_token';
const USER_KEY = 'zonara_user';

/**
 * Mengambil access token dari localStorage.
 * @returns {string|null} Access token JWT.
 */
export function getToken() {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

/**
 * Mengambil data user dari localStorage.
 * @returns {object|null} Objek user terdeserialisasi.
 */
export function getUser() {
  try {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

/**
 * Menyimpan data autentikasi ke localStorage.
 * @param {object} params - { user, accessToken, refreshToken }
 */
export function saveAuth({ user, accessToken, refreshToken }) {
  try {
    if (accessToken) localStorage.setItem(TOKEN_KEY, accessToken);
    if (refreshToken) localStorage.setItem(REFRESH_KEY, refreshToken);
    if (user) localStorage.setItem(USER_KEY, JSON.stringify(user));
  } catch (err) {
    console.error('Failed to save auth data:', err);
  }
}

/**
 * Menghapus seluruh data autentikasi dari localStorage.
 */
export function clearAuth() {
  try {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(USER_KEY);
  } catch (err) {
    console.error('Failed to clear auth data:', err);
  }
}

/**
 * Memformat tanggal ke format Indonesia.
 * @param {string} dateStr - ISO date string.
 * @returns {string} Tanggal terformat (e.g., "25 Maret 2026").
 */
export function formatDateID(dateStr) {
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString('id-ID', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

/**
 * Memformat waktu ke format Indonesia.
 * @param {string} dateStr - ISO date string.
 * @returns {string} Waktu terformat (e.g., "14:30 WIB").
 */
export function formatTimeID(dateStr) {
  try {
    const date = new Date(dateStr);
    return date.toLocaleTimeString('id-ID', {
      hour: '2-digit',
      minute: '2-digit',
    }) + ' WIB';
  } catch {
    return dateStr;
  }
}

/**
 * Menghitung persentase skor dari total percobaan.
 * @param {number} score - Skor yang diperoleh.
 * @param {number} total - Total percobaan.
 * @returns {number} Persentase (0-100).
 */
export function calculatePercentage(score, total) {
  if (total === 0) return 0;
  return Math.round((score / total) * 100);
}

/**
 * Mapping label positif untuk zona (positive framing per FR-006.5).
 * @param {number} score - Skor siswa.
 * @param {number} avg - Rata-rata kelas.
 * @returns {string} Label positif.
 */
export function getPositiveLabel(score, avg) {
  if (avg === 0) return 'Belum Dinilai';
  const ratio = score / avg;
  if (ratio >= 1.0) return 'Area Kekuatan';
  if (ratio >= 0.8) return 'Berkembang Baik';
  return 'Area Pertumbuhan';
}
