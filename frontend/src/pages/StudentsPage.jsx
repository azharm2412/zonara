/**
 * @module StudentsPage
 * @desc Halaman manajemen data siswa: daftar siswa per kelas dan tambah siswa baru.
 * @author Azhar Maulana
 * @date 25 Maret 2026
 * @version 1.0
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

import {
  useGetStudentsQuery,
  useCreateStudentMutation,
} from '../store/apiSlice';

/**
 * Komponen halaman Data Siswa.
 * @returns {JSX.Element} Halaman Students.
 */
function StudentsPage() {
  const [className, setClassName] = useState('5A');
  const [showForm, setShowForm] = useState(false);
  const [newStudent, setNewStudent] = useState({ full_name: '', nis: '' });

  const { data: studentsData, isLoading } = useGetStudentsQuery(className);
  const [createStudent, { isLoading: creating }] = useCreateStudentMutation();

  const students = studentsData?.data?.students || [];

  /**
   * Handler untuk menambah siswa baru.
   */
  const handleCreateStudent = async (e) => {
    e.preventDefault();
    if (!newStudent.full_name.trim()) {
      toast.error('Nama siswa harus diisi.');
      return;
    }

    try {
      await createStudent({
        full_name: newStudent.full_name.trim(),
        nis: newStudent.nis.trim() || null,
        class_name: className,
      }).unwrap();

      toast.success(`Siswa "${newStudent.full_name}" berhasil ditambahkan!`);
      setNewStudent({ full_name: '', nis: '' });
      setShowForm(false);
    } catch (err) {
      toast.error(err?.data?.detail || 'Gagal menambahkan siswa.');
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="p-6 lg:p-8 max-w-5xl mx-auto"
    >
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-display font-bold text-white">
          Data Siswa
        </h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="btn-primary text-sm"
        >
          {showForm ? '✕ Tutup' : '+ Tambah Siswa'}
        </button>
      </div>

      {/* Filter Kelas */}
      <div className="mb-6 glass-card p-4">
        <label className="text-sm text-surface-200 mb-2 block">Filter Kelas</label>
        <div className="flex flex-wrap gap-2">
          {['1A', '1B', '2A', '2B', '3A', '3B', '4A', '4B', '5A', '5B', '6A', '6B'].map((c) => (
            <button
              key={c}
              onClick={() => setClassName(c)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                className === c
                  ? 'bg-zona-blue-500/20 text-zona-blue-400 border border-zona-blue-500/50 ring-1 ring-zona-blue-400/30'
                  : 'bg-surface-700/30 text-surface-200/60 border border-surface-600 hover:bg-surface-700/50'
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      {/* Form Tambah Siswa */}
      {showForm && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 glass-card p-6"
        >
          <h2 className="text-lg font-semibold text-white mb-4">Tambah Siswa ke Kelas {className}</h2>
          <form onSubmit={handleCreateStudent} className="flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              placeholder="Nama Lengkap *"
              value={newStudent.full_name}
              onChange={(e) => setNewStudent({ ...newStudent, full_name: e.target.value })}
              className="input-field flex-1"
              required
            />
            <input
              type="text"
              placeholder="NIS (opsional)"
              value={newStudent.nis}
              onChange={(e) => setNewStudent({ ...newStudent, nis: e.target.value })}
              className="input-field w-40"
            />
            <button
              type="submit"
              disabled={creating}
              className="btn-primary whitespace-nowrap"
            >
              {creating ? 'Menyimpan...' : 'Simpan'}
            </button>
          </form>
        </motion.div>
      )}

      {/* Tabel Siswa */}
      <div className="glass-card p-6">
        <h2 className="text-lg font-semibold text-white mb-4">
          Siswa Kelas {className}
          <span className="text-xs text-surface-200/40 ml-2">({students.length} siswa)</span>
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-surface-200/60 border-b border-surface-700">
                <th className="text-left py-3 px-4 w-12">#</th>
                <th className="text-left py-3 px-4">Nama Lengkap</th>
                <th className="text-left py-3 px-4">NIS</th>
                <th className="text-left py-3 px-4">Kelas</th>
              </tr>
            </thead>
            <tbody>
              {students.map((s, idx) => (
                <tr key={s.id} className="border-b border-surface-700/50 hover:bg-surface-700/20 transition-colors">
                  <td className="py-3 px-4 text-surface-200/50">{idx + 1}</td>
                  <td className="py-3 px-4 text-surface-100 font-medium">{s.full_name}</td>
                  <td className="py-3 px-4 font-mono text-zona-blue-400 text-xs">{s.nis || '—'}</td>
                  <td className="py-3 px-4 text-surface-200">{s.class_name}</td>
                </tr>
              ))}
              {students.length === 0 && (
                <tr>
                  <td colSpan="4" className="py-8 text-center text-surface-200/40">
                    {isLoading ? 'Memuat...' : 'Belum ada siswa di kelas ini.'}
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

export default StudentsPage;
