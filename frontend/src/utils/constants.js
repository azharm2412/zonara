/**
 * @module Constants
 * @desc Konstanta global: warna zona, role definitions, API endpoints.
 * @author Azhar Maulana
 * @date 25 Maret 2026
 * @version 1.0
 */

/** Palet warna 4 zona karakter CASEL */
export const ZONE_COLORS = {
  blue: { hex: '#3B82F6', name: 'Self-Awareness', label: 'Biru', dimension: 'Kesadaran Diri' },
  green: { hex: '#22C55E', name: 'Relationship Skills', label: 'Hijau', dimension: 'Keterampilan Relasi' },
  yellow: { hex: '#F59E0B', name: 'Self-Management', label: 'Kuning', dimension: 'Pengelolaan Diri' },
  red: { hex: '#EF4444', name: 'Social Awareness', label: 'Merah', dimension: 'Kesadaran Sosial' },
};

/** Warna aksen emas untuk badge/prestasi */
export const GOLD_ACCENT = '#D4AF37';

/** Definisi peran RBAC dengan label dan permissions */
export const ROLES = {
  admin: { label: 'Administrator', permissions: ['all'] },
  guru_bk: { label: 'Guru BK', permissions: ['sessions', 'scan', 'students', 'analytics', 'export'] },
  wali_kelas: { label: 'Wali Kelas', permissions: ['analytics', 'students'] },
  orang_tua: { label: 'Orang Tua', permissions: ['analytics'] },
};

/** Menu sidebar berdasarkan role */
export const SIDEBAR_MENU = [
  { key: 'dashboard', label: 'Dashboard', path: '/dashboard', roles: ['admin', 'guru_bk', 'wali_kelas', 'orang_tua'] },
  { key: 'sessions', label: 'Sesi Permainan', path: '/sessions', roles: ['admin', 'guru_bk'] },
  { key: 'students', label: 'Data Siswa', path: '/students', roles: ['admin', 'guru_bk', 'wali_kelas'] },
];

/** Threshold flag intervensi (skor < 80% rata-rata kelas) */
export const FLAG_THRESHOLD = 0.80;

/** Konfigurasi WebSocket reconnection */
export const WS_RECONNECT = {
  initialDelay: 1000,
  maxDelay: 30000,
  factor: 2,
};
