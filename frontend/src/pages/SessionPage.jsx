/**
 * @module SessionPage
 * @desc Halaman manajemen sesi permainan: buat sesi baru, QR scan 2-step, daftar sesi.
 *       
 *       v1.2 — KRENOVA Demo Fix:
 *       - 2-Step Scan Flow: Lookup kartu → tampilkan info → guru konfirmasi Berhasil/Gagal
 *       - Card Info Preview: judul tantangan, zona (warna), deskripsi
 *       - Auto-close sesi lama di backend (transparan)
 *       - Scan history log + success toast yang informatif
 *
 * @author Azhar Maulana
 * @date 25 Maret 2026
 * @version 1.2
 */

import React, { useState, useEffect, useMemo } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';

import QRScanner from '../components/QRScanner';
import {
  useGetSessionsQuery,
  useCreateSessionMutation,
  useEndSessionMutation,
  useLookupCardMutation,
  useConfirmScoreMutation,
  useGetStudentsQuery,
} from '../store/apiSlice';

/**
 * Komponen halaman sesi permainan.
 * @returns {JSX.Element} Halaman Session.
 */
function SessionPage() {
  const { user } = useSelector((state) => state.auth);
  const navigate = useNavigate();

  // -- Session creation state --
  const [className, setClassName] = useState('5A');
  const [selectedStudentIds, setSelectedStudentIds] = useState([]);

  // -- Active session state --
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [activeSessionPlayers, setActiveSessionPlayers] = useState([]);
  const [scannerVisible, setScannerVisible] = useState(false);
  const [selectedStudentForScan, setSelectedStudentForScan] = useState(null);

  // -- 2-Step Scan state --
  const [pendingCard, setPendingCard] = useState(null);  // Info kartu yang sedang ditampilkan
  const [scanHistory, setScanHistory] = useState([]);

  // -- API hooks --
  const { data: sessionsData, isLoading: sessionsLoading } = useGetSessionsQuery();
  const { data: studentsData } = useGetStudentsQuery(className);
  const [createSession, { isLoading: creating }] = useCreateSessionMutation();
  const [endSession] = useEndSessionMutation();
  const [lookupCard, { isLoading: lookingUp }] = useLookupCardMutation();
  const [confirmScore, { isLoading: confirming }] = useConfirmScoreMutation();

  const sessions = sessionsData?.data?.sessions || [];
  const students = studentsData?.data?.students || [];

  /**
   * Auto-resume: Saat halaman dimuat, cari sesi aktif dari riwayat.
   */
  useEffect(() => {
    if (!activeSessionId && sessions.length > 0) {
      const activeSession = sessions.find((s) => s.status === 'active');
      if (activeSession) {
        setActiveSessionId(activeSession.id);
      }
    }
  }, [sessions, activeSessionId]);

  /**
   * Daftar siswa untuk dropdown scan.
   */
  const playersForScan = useMemo(() => {
    if (activeSessionPlayers.length > 0) {
      return students.filter((s) => activeSessionPlayers.includes(s.id));
    }
    return students;
  }, [students, activeSessionPlayers]);

  /**
   * Handler buat sesi baru (backend auto-close sesi lama).
   */
  const handleCreateSession = async () => {
    if (selectedStudentIds.length === 0) {
      toast.error('Pilih minimal 1 siswa untuk memulai sesi.');
      return;
    }

    try {
      const result = await createSession({
        class_name: className,
        student_ids: selectedStudentIds,
      }).unwrap();

      toast.success(result.message || 'Sesi berhasil dibuat!');
      setActiveSessionId(result.data.session_id);
      setActiveSessionPlayers([...selectedStudentIds]);
      setSelectedStudentIds([]);
      setScanHistory([]);
      setPendingCard(null);
    } catch (err) {
      toast.error(err?.data?.detail || 'Gagal membuat sesi.');
    }
  };

  /**
   * Handler akhiri sesi.
   */
  const handleEndSession = async (sessionId) => {
    try {
      const result = await endSession(sessionId).unwrap();
      toast.success(result.message || 'Sesi berhasil diakhiri.');
      setActiveSessionId(null);
      setActiveSessionPlayers([]);
      setScannerVisible(false);
      setSelectedStudentForScan(null);
      setScanHistory([]);
      setPendingCard(null);
    } catch (err) {
      toast.error(err?.data?.detail || 'Gagal mengakhiri sesi.');
    }
  };

  /**
   * STEP 1: Lookup kartu dari QR code.
   * Menampilkan info kartu ke guru TANPA mencatat skor.
   *
   * @param {string} qrCode - String QR yang dipindai/diketik manual.
   */
  const handleQRScan = async (qrCode) => {
    if (!activeSessionId) {
      toast.error('Tidak ada sesi aktif.');
      return;
    }
    if (!selectedStudentForScan) {
      toast.error('Pilih siswa terlebih dahulu.');
      return;
    }

    try {
      const result = await lookupCard({
        session_id: activeSessionId,
        student_id: selectedStudentForScan,
        qr_code: qrCode,
      }).unwrap();

      // Tampilkan info kartu ke guru — belum catat skor
      setPendingCard({
        ...result.data,
        studentId: selectedStudentForScan,
        studentName: playersForScan.find(
          (s) => s.id === selectedStudentForScan
        )?.full_name || `ID ${selectedStudentForScan}`,
      });

      toast.success(`📋 Kartu ditemukan: "${result.data.title}"`);
    } catch (err) {
      toast.error(err?.data?.detail || 'Gagal mencari kartu. Cek kode QR.');
      setPendingCard(null);
    }
  };

  /**
   * STEP 2: Guru konfirmasi hasil (Berhasil / Gagal) dan catat skor.
   *
   * @param {number} resultValue - 1 = Berhasil, 0 = Gagal/Perlu Bimbingan.
   */
  const handleConfirmResult = async (resultValue) => {
    if (!pendingCard || !activeSessionId) return;

    try {
      const result = await confirmScore({
        session_id: activeSessionId,
        student_id: pendingCard.studentId,
        card_id: pendingCard.card_id,
        zone_id: pendingCard.zone_id,
        result: resultValue,
      }).unwrap();

      const statusLabel = resultValue === 1 ? '✓ Berhasil' : '○ Perlu Bimbingan';

      toast.success(
        `Skor dicatat! ${pendingCard.studentName} — ${pendingCard.zone_name}: ${statusLabel}`,
        { duration: 4000, icon: '🎯' }
      );

      // Tambahkan ke scan history
      setScanHistory((prev) => [
        {
          id: Date.now(),
          studentName: pendingCard.studentName,
          qrCode: pendingCard.qr_code,
          cardTitle: pendingCard.title,
          zoneName: pendingCard.zone_name,
          zoneColor: pendingCard.zone_color,
          result: resultValue,
          time: new Date().toLocaleTimeString('id-ID'),
        },
        ...prev,
      ]);

      // Reset pending card
      setPendingCard(null);
    } catch (err) {
      toast.error(err?.data?.detail || 'Gagal mencatat skor.');
    }
  };

  /**
   * Toggle student selection.
   */
  const toggleStudent = (studentId) => {
    setSelectedStudentIds((prev) =>
      prev.includes(studentId)
        ? prev.filter((id) => id !== studentId)
        : [...prev, studentId]
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="p-6 lg:p-8 max-w-7xl mx-auto"
    >
      <h1 className="text-3xl font-display font-bold text-white mb-6">
        Sesi Permainan
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* =========== CREATE SESSION PANEL =========== */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Buat Sesi Baru</h2>

          <div className="mb-4">
            <label className="text-sm text-surface-200 mb-1 block">Kelas</label>
            <select
              id="session-class-selector"
              value={className}
              onChange={(e) => setClassName(e.target.value)}
              className="input-field w-full"
            >
              {['1A', '1B', '2A', '2B', '3A', '3B', '4A', '4B', '5A', '5B', '6A', '6B'].map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          {/* Student Checklist */}
          <div className="mb-4 max-h-48 overflow-y-auto space-y-2">
            {students.length > 0 ? students.map((s) => (
              <label
                key={s.id}
                className="flex items-center gap-3 p-2 rounded-lg hover:bg-surface-700/30 cursor-pointer transition-colors"
              >
                <input
                  type="checkbox"
                  checked={selectedStudentIds.includes(s.id)}
                  onChange={() => toggleStudent(s.id)}
                  className="w-4 h-4 rounded border-surface-600 text-zona-blue-500 focus:ring-zona-blue-400"
                />
                <span className="text-sm text-surface-100">{s.full_name}</span>
              </label>
            )) : (
              <p className="text-sm text-surface-200/40">Belum ada siswa di kelas ini.</p>
            )}
          </div>

          <button
            onClick={handleCreateSession}
            disabled={creating || selectedStudentIds.length === 0}
            className="btn-primary w-full"
          >
            {creating ? 'Membuat...' : `Mulai Sesi (${selectedStudentIds.length} siswa)`}
          </button>
        </div>

        {/* =========== QR SCANNER PANEL =========== */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold text-white mb-4">QR Scanner</h2>

          {activeSessionId ? (
            <>
              {/* Pilih Siswa */}
              <div className="mb-4">
                <label className="text-sm text-surface-200 mb-1 block">Pilih Siswa untuk Dinilai</label>
                <select
                  id="scan-student-selector"
                  value={selectedStudentForScan || ''}
                  onChange={(e) => {
                    setSelectedStudentForScan(Number(e.target.value));
                    setPendingCard(null); // Reset preview saat ganti siswa
                  }}
                  className="input-field w-full"
                >
                  <option value="">-- Pilih Siswa --</option>
                  {playersForScan.map((s) => (
                    <option key={s.id} value={s.id}>{s.full_name}</option>
                  ))}
                </select>
              </div>

              {/* QR Scanner Component */}
              <QRScanner onScanResult={handleQRScan} active={scannerVisible} />

              {/* Loading indicator saat lookup */}
              {lookingUp && (
                <div className="mt-3 flex items-center gap-2 text-zona-blue-400">
                  <div className="w-4 h-4 border-2 border-zona-blue-400 border-t-transparent rounded-full animate-spin" />
                  <span className="text-sm">Mencari kartu...</span>
                </div>
              )}

              {/* =========== CARD INFO PREVIEW (Step 1 Result) =========== */}
              <AnimatePresence>
                {pendingCard && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="mt-4 rounded-xl border-2 overflow-hidden"
                    style={{ borderColor: pendingCard.zone_color || '#6B7280' }}
                  >
                    {/* Card Header */}
                    <div
                      className="px-4 py-3 flex items-center justify-between"
                      style={{ backgroundColor: `${pendingCard.zone_color}20` }}
                    >
                      <div>
                        <p className="text-xs font-medium text-surface-200/60 mb-0.5">
                          📋 Kartu Tantangan — {pendingCard.zone_name}
                        </p>
                        <h3 className="text-lg font-bold text-white">
                          {pendingCard.title}
                        </h3>
                      </div>
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: pendingCard.zone_color }}
                      />
                    </div>

                    {/* Card Body */}
                    <div className="px-4 py-3 space-y-2 bg-surface-800/50">
                      <div>
                        <p className="text-xs text-surface-200/50">Apa yang harus dilakukan:</p>
                        <p className="text-sm text-surface-100 mt-1">
                          {pendingCard.description || 'Tidak ada deskripsi.'}
                        </p>
                      </div>
                      <div className="flex gap-4 text-xs text-surface-200/50">
                        <span>Zona: <strong style={{ color: pendingCard.zone_color }}>{pendingCard.zone_name}</strong></span>
                        {pendingCard.difficulty && (
                          <span>Tingkat: <strong className="text-surface-100">{pendingCard.difficulty}</strong></span>
                        )}
                      </div>
                      <p className="text-xs text-surface-200/40">
                        Siswa: <strong className="text-surface-100">{pendingCard.studentName}</strong>
                      </p>
                    </div>

                    {/* Confirmation Buttons (Step 2) */}
                    <div className="px-4 py-3 flex gap-3 bg-surface-800/30 border-t border-surface-700/50">
                      <button
                        onClick={() => handleConfirmResult(1)}
                        disabled={confirming}
                        className="flex-1 py-3 px-4 rounded-lg text-sm font-bold transition-all 
                          bg-zona-green-500/20 text-zona-green-400 border border-zona-green-500/50 
                          hover:bg-zona-green-500/30 hover:ring-2 hover:ring-zona-green-400/30
                          disabled:opacity-50"
                      >
                        {confirming ? '...' : '✓ Berhasil'}
                      </button>
                      <button
                        onClick={() => handleConfirmResult(0)}
                        disabled={confirming}
                        className="flex-1 py-3 px-4 rounded-lg text-sm font-bold transition-all 
                          bg-zona-yellow-500/20 text-zona-yellow-400 border border-zona-yellow-500/50 
                          hover:bg-zona-yellow-500/30 hover:ring-2 hover:ring-zona-yellow-400/30
                          disabled:opacity-50"
                      >
                        {confirming ? '...' : '○ Perlu Bimbingan'}
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Scanner Controls */}
              <div className="flex gap-3 mt-4">
                <button
                  onClick={() => setScannerVisible(!scannerVisible)}
                  className="btn-secondary flex-1"
                >
                  {scannerVisible ? '⏹ Tutup Scanner' : '▶ Buka Scanner'}
                </button>
                <button
                  onClick={() => handleEndSession(activeSessionId)}
                  className="btn-danger flex-1"
                >
                  Akhiri Sesi
                </button>
              </div>
            </>
          ) : (
            <div className="h-48 flex items-center justify-center text-surface-200/40">
              Buat sesi terlebih dahulu untuk mulai memindai.
            </div>
          )}
        </div>
      </div>

      {/* =========== SCAN HISTORY =========== */}
      {activeSessionId && scanHistory.length > 0 && (
        <div className="mt-6 glass-card p-6">
          <h2 className="text-lg font-semibold text-white mb-4">
            📋 Log Scan Sesi Aktif
            <span className="text-xs text-surface-200/40 ml-2">({scanHistory.length} scan)</span>
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-surface-200/60 border-b border-surface-700">
                  <th className="text-left py-2 px-3">Waktu</th>
                  <th className="text-left py-2 px-3">Siswa</th>
                  <th className="text-left py-2 px-3">Tantangan</th>
                  <th className="text-left py-2 px-3">Zona</th>
                  <th className="text-left py-2 px-3">Hasil</th>
                </tr>
              </thead>
              <tbody>
                {scanHistory.map((log) => (
                  <tr key={log.id} className="border-b border-surface-700/50">
                    <td className="py-2 px-3 text-surface-200/60 text-xs">{log.time}</td>
                    <td className="py-2 px-3 text-surface-100">{log.studentName}</td>
                    <td className="py-2 px-3 text-surface-200 text-xs">{log.cardTitle}</td>
                    <td className="py-2 px-3">
                      <span className="flex items-center gap-1.5">
                        <span
                          className="w-2 h-2 rounded-full inline-block"
                          style={{ backgroundColor: log.zoneColor || '#6B7280' }}
                        />
                        <span className="text-surface-200 text-xs">{log.zoneName}</span>
                      </span>
                    </td>
                    <td className="py-2 px-3">
                      <span className={`text-xs font-medium ${
                        log.result === 1 ? 'text-zona-green-400' : 'text-zona-yellow-400'
                      }`}>
                        {log.result === 1 ? '✓ Berhasil' : '○ Perlu Bimbingan'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* =========== SESSIONS HISTORY =========== */}
      <div className="mt-6 glass-card p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Riwayat Sesi</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-surface-200/60 border-b border-surface-700">
                <th className="text-left py-3 px-4">Kode Sesi</th>
                <th className="text-left py-3 px-4">Kelas</th>
                <th className="text-left py-3 px-4">Status</th>
                <th className="text-left py-3 px-4">Aksi</th>
              </tr>
            </thead>
            <tbody>
              {sessions.map((s) => (
                <tr key={s.id} className="border-b border-surface-700/50 hover:bg-surface-700/20 transition-colors">
                  <td className="py-3 px-4 font-mono text-zona-blue-400">{s.session_code}</td>
                  <td className="py-3 px-4 text-surface-200">{s.class_name}</td>
                  <td className="py-3 px-4">
                    <span className={`badge-zona ${s.status === 'active' ? 'bg-zona-green-500/20 text-zona-green-400' : 'bg-surface-600/30 text-surface-200/50'}`}>
                      {s.status === 'active' ? '● Aktif' : '✓ Selesai'}
                    </span>
                  </td>
                  <td className="py-3 px-4 flex gap-2">
                    {s.status === 'active' && (
                      <>
                        <button
                          onClick={() => {
                            setActiveSessionId(s.id);
                            setActiveSessionPlayers([]);
                            setScanHistory([]);
                            setPendingCard(null);
                          }}
                          className="text-xs text-zona-green-400 hover:underline"
                        >
                          Resume Scan
                        </button>
                        <button
                          onClick={() => navigate(`/focus/${s.id}`)}
                          className="text-xs text-zona-blue-400 hover:underline"
                        >
                          Focus Mode →
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
              {sessions.length === 0 && (
                <tr>
                  <td colSpan="4" className="py-8 text-center text-surface-200/40">
                    {sessionsLoading ? 'Memuat...' : 'Belum ada sesi permainan.'}
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

export default SessionPage;
