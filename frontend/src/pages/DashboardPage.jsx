/**
 * @module DashboardPage
 * @desc Halaman utama dashboard dengan Radar Chart, daftar flag intervensi,
 *       dan ringkasan kelas. Tampilan berbeda berdasarkan role.
 * @author Azhar Maulana
 * @date 25 Maret 2026
 * @version 1.0
 */

import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import { motion } from 'framer-motion';

import RadarChart from '../components/RadarChart';
import { useGetClassSummaryQuery, useGetStudentsQuery } from '../store/apiSlice';
import { ZONE_COLORS } from '../utils/constants';
import { getPositiveLabel } from '../utils/helpers';

/**
 * Komponen halaman Dashboard dengan ringkasan analitik.
 * @returns {JSX.Element} Halaman Dashboard.
 */
function DashboardPage() {
  const { user } = useSelector((state) => state.auth);
  const [selectedClass, setSelectedClass] = useState('5A');

  const { data: summaryData, isLoading: summaryLoading } = useGetClassSummaryQuery(selectedClass, {
    skip: !user || user.role === 'orang_tua',
  });

  const { data: studentsData } = useGetStudentsQuery(selectedClass, {
    skip: !user,
  });

  const classSummary = summaryData?.data;
  const students = studentsData?.data?.students || [];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="p-6 lg:p-8 max-w-7xl mx-auto"
    >
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-display font-bold text-white mb-2">
          Dashboard Analitik
        </h1>
        <p className="text-surface-200/60">
          Selamat datang, <span className="text-zona-blue-400 font-medium">{user?.full_name}</span>
        </p>
      </div>

      {/* Class Selector (non orang_tua) */}
      {user?.role !== 'orang_tua' && (
        <div className="mb-6 flex items-center gap-4">
          <label className="text-sm font-medium text-surface-200">Kelas:</label>
          <select
            id="class-selector"
            value={selectedClass}
            onChange={(e) => setSelectedClass(e.target.value)}
            className="input-field w-32"
          >
            {['1A', '1B', '2A', '2B', '3A', '3B', '4A', '4B', '5A', '5B', '6A', '6B'].map((cls) => (
              <option key={cls} value={cls}>{cls}</option>
            ))}
          </select>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {Object.entries(ZONE_COLORS).map(([code, zone]) => (
          <motion.div
            key={code}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card p-5"
          >
            <div className="flex items-center justify-between mb-3">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: zone.hex }}
              />
              <span className="text-xs text-surface-200/50">{zone.label}</span>
            </div>
            <p className="text-2xl font-bold text-white">
              {classSummary?.class_average?.[code]?.toFixed(1) ?? '—'}
            </p>
            <p className="text-sm text-surface-200/60 mt-1">{zone.name}</p>
          </motion.div>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Radar Chart */}
        <div className="lg:col-span-2 glass-card p-6">
          <h2 className="text-lg font-semibold text-white mb-4">
            Rata-rata Kelas — Radar Chart
          </h2>
          {classSummary?.class_average ? (
            <RadarChart data={classSummary.class_average} />
          ) : (
            <div className="h-64 flex items-center justify-center text-surface-200/40">
              {summaryLoading ? 'Memuat data...' : 'Belum ada data skor untuk kelas ini.'}
            </div>
          )}
        </div>

        {/* Flagged Students */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold text-white mb-4">
            ⚠️ Area Pertumbuhan
          </h2>
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {classSummary?.flagged_students?.length > 0 ? (
              classSummary.flagged_students.map((student) => (
                <div
                  key={student.student_id}
                  className="p-3 bg-surface-700/30 rounded-xl border border-zona-red-500/20"
                >
                  <p className="text-sm font-medium text-white">{student.name}</p>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {student.flags.map((flag) => (
                      <span
                        key={flag}
                        className="badge-zona text-white"
                        style={{ backgroundColor: ZONE_COLORS[flag]?.hex + '30', color: ZONE_COLORS[flag]?.hex }}
                      >
                        {ZONE_COLORS[flag]?.label || flag}
                      </span>
                    ))}
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-surface-200/40">
                {summaryLoading ? 'Memuat...' : 'Tidak ada siswa yang memerlukan intervensi. 🎉'}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Student List */}
      <div className="mt-6 glass-card p-6">
        <h2 className="text-lg font-semibold text-white mb-4">
          Daftar Siswa — Kelas {selectedClass}
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-surface-200/60 border-b border-surface-700">
                <th className="text-left py-3 px-4">No</th>
                <th className="text-left py-3 px-4">NIS</th>
                <th className="text-left py-3 px-4">Nama Lengkap</th>
                <th className="text-left py-3 px-4">Kelas</th>
              </tr>
            </thead>
            <tbody>
              {students.length > 0 ? (
                students.map((s, idx) => (
                  <tr key={s.id} className="border-b border-surface-700/50 hover:bg-surface-700/20 transition-colors">
                    <td className="py-3 px-4 text-surface-200">{idx + 1}</td>
                    <td className="py-3 px-4 text-surface-200">{s.nis || '—'}</td>
                    <td className="py-3 px-4 text-white font-medium">{s.full_name}</td>
                    <td className="py-3 px-4 text-surface-200">{s.class_name}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="4" className="py-8 text-center text-surface-200/40">
                    Belum ada data siswa.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </motion.div>
  );
}

export default DashboardPage;
