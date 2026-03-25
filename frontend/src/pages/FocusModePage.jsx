/**
 * @module FocusModePage
 * @desc Halaman full-screen presentation mode untuk proyektor.
 *       Menampilkan Radar Chart dan live score.
 *
 *       v1.2 — KRENOVA Demo Fix:
 *       - Langsung fetch data via REST saat mount (bukan tunggu WS)
 *       - Polling setiap 3 detik untuk update realtime
 *       - Tampilkan session info dan total scan
 *
 * @author Azhar Maulana
 * @date 25 Maret 2026
 * @version 1.2
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

import RadarChart from '../components/RadarChart';
import { ZONE_COLORS } from '../utils/constants';
import { getToken } from '../utils/helpers';

/** Interval polling (ms) — 3 detik untuk demo responsif */
const POLL_INTERVAL_MS = 3000;

/**
 * Komponen Focus Mode — tampilan proyektor full-screen.
 * Data diambil langsung via REST polling (lebih stabil untuk demo).
 *
 * @returns {JSX.Element} Halaman Focus Mode.
 */
function FocusModePage() {
  const { sessionId } = useParams();
  const navigate = useNavigate();

  const [radarData, setRadarData] = useState({ blue: 0, green: 0, yellow: 0, red: 0 });
  const [totalScans, setTotalScans] = useState(0);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('loading');
  const [errorMsg, setErrorMsg] = useState(null);

  /**
   * Fetch data radar dari REST endpoint.
   * Menggunakan token dari helpers.js (konsisten dengan apiSlice).
   */
  const fetchRadarData = useCallback(async () => {
    const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
    const token = getToken();

    try {
      const response = await fetch(
        `${apiBase}/analytics/session-radar/${sessionId}`,
        {
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
        }
      );

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData?.detail || `HTTP ${response.status}`);
      }

      const data = await response.json();

      if (data?.data?.radar_data) {
        setRadarData(data.data.radar_data);
        setTotalScans(data.data.total_scans || 0);
        setLastUpdate(new Date().toLocaleTimeString('id-ID'));
        setConnectionStatus('connected');
        setErrorMsg(null);
      }
    } catch (err) {
      console.error('Focus Mode fetch error:', err);
      setConnectionStatus('error');
      setErrorMsg(err.message);
    }
  }, [sessionId]);

  /**
   * Fetch data segera saat mount + polling berkala.
   */
  useEffect(() => {
    // Immediate fetch
    fetchRadarData();

    // Polling interval
    const intervalId = setInterval(fetchRadarData, POLL_INTERVAL_MS);

    return () => clearInterval(intervalId);
  }, [fetchRadarData]);

  /**
   * Exit Focus Mode via Escape key.
   */
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') {
        navigate('/sessions');
      }
    };
    document.addEventListener('keydown', handleEsc);
    return () => document.removeEventListener('keydown', handleEsc);
  }, [navigate]);

  /** Status indicator color */
  const getStatusColor = () => {
    if (connectionStatus === 'connected') return 'bg-zona-green-500 animate-pulse';
    if (connectionStatus === 'loading') return 'bg-zona-yellow-500 animate-pulse';
    return 'bg-zona-red-500';
  };

  const getStatusLabel = () => {
    if (connectionStatus === 'connected') return `Live (${POLL_INTERVAL_MS / 1000}s)`;
    if (connectionStatus === 'loading') return 'Memuat...';
    return 'Error';
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="fixed inset-0 bg-surface-900 z-50 flex flex-col items-center justify-center p-8"
    >
      {/* Status Indicator */}
      <div className="absolute top-4 right-4 flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${getStatusColor()}`} />
        <span className="text-xs text-surface-200/50">{getStatusLabel()}</span>
      </div>

      {/* Exit hint + Back button */}
      <div className="absolute top-4 left-4 flex items-center gap-3">
        <button
          onClick={() => navigate('/sessions')}
          className="text-xs text-surface-200/50 hover:text-surface-200 transition-colors"
        >
          ← Kembali
        </button>
        <span className="text-xs text-surface-200/20">| ESC</span>
      </div>

      {/* Title */}
      <motion.h1
        className="text-5xl font-display font-bold gradient-text mb-2"
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        Zonara
      </motion.h1>
      <p className="text-surface-200/50 mb-8 text-lg">
        Sesi: <span className="text-zona-blue-400 font-mono">{sessionId}</span>
        {totalScans > 0 && (
          <span className="text-surface-200/30 ml-3 text-sm">({totalScans} scan)</span>
        )}
      </p>

      {/* Error Message */}
      {errorMsg && (
        <div className="mb-4 px-4 py-2 rounded-lg bg-zona-red-500/10 border border-zona-red-500/30">
          <p className="text-xs text-zona-red-400">⚠ {errorMsg}</p>
        </div>
      )}

      {/* Radar Chart — Large */}
      <motion.div
        className="w-full max-w-2xl"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.4, type: 'spring' }}
      >
        <RadarChart data={radarData} size="large" />
      </motion.div>

      {/* Zone Scores */}
      <div className="flex gap-8 mt-8">
        {Object.entries(ZONE_COLORS).map(([code, zone]) => (
          <motion.div
            key={code}
            className="text-center"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.6 }}
          >
            <div
              className="w-4 h-4 rounded-full mx-auto mb-2"
              style={{ backgroundColor: zone.hex }}
            />
            <p className="text-3xl font-bold text-white">{radarData[code] ?? 0}</p>
            <p className="text-xs text-surface-200/50 mt-1">{zone.label}</p>
          </motion.div>
        ))}
      </div>

      {/* Last update */}
      {lastUpdate && (
        <p className="absolute bottom-4 text-xs text-surface-200/30">
          Update terakhir: {lastUpdate}
        </p>
      )}
    </motion.div>
  );
}

export default FocusModePage;
