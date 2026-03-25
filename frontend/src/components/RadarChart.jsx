/**
 * @module RadarChart
 * @desc Komponen Radar Chart interaktif menggunakan Recharts + Framer Motion.
 *       Memvisualisasikan profil karakter siswa dalam 4 dimensi CASEL.
 * @author Azhar Maulana
 * @date 25 Maret 2026
 * @version 1.0
 */

import React from 'react';
import { motion } from 'framer-motion';
import {
  RadarChart as RechartsRadar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import { ZONE_COLORS } from '../utils/constants';

/**
 * Komponen Radar Chart untuk visualisasi skor karakter.
 *
 * @param {object} props
 * @param {object} props.data - Skor per zona (e.g., { blue: 3, green: 2, yellow: 3, red: 1 }).
 * @param {object} [props.classAverage] - Rata-rata kelas untuk overlay (opsional).
 * @param {string} [props.size] - Ukuran chart: 'normal' atau 'large'.
 * @returns {JSX.Element} Radar Chart.
 */
function RadarChart({ data = {}, classAverage = null, size = 'normal' }) {
  /**
   * Transform data untuk format Recharts.
   * @returns {Array} Data series untuk Recharts.
   */
  const chartData = Object.entries(ZONE_COLORS).map(([code, zone]) => ({
    dimension: zone.label,
    score: data[code] ?? 0,
    classAvg: classAverage?.[code] ?? null,
    fullMark: 10,
    color: zone.hex,
  }));

  const height = size === 'large' ? 500 : 320;

  return (
    <motion.div
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.5, type: 'spring' }}
      className="w-full animate-radar-pulse"
    >
      <ResponsiveContainer width="100%" height={height}>
        <RechartsRadar cx="50%" cy="50%" outerRadius="80%" data={chartData}>
          {/* Grid */}
          <PolarGrid
            stroke="#334155"
            strokeDasharray="3 3"
          />

          {/* Axis Labels */}
          <PolarAngleAxis
            dataKey="dimension"
            tick={{
              fill: '#94A3B8',
              fontSize: size === 'large' ? 14 : 11,
              fontWeight: 500,
            }}
          />

          {/* Radius Scale */}
          <PolarRadiusAxis
            angle={90}
            domain={[0, 10]}
            tick={{ fill: '#475569', fontSize: 10 }}
            tickCount={6}
          />

          {/* Class Average Overlay (jika ada) */}
          {classAverage && (
            <Radar
              name="Rata-rata Kelas"
              dataKey="classAvg"
              stroke="#D4AF37"
              fill="#D4AF37"
              fillOpacity={0.1}
              strokeWidth={1.5}
              strokeDasharray="4 4"
            />
          )}

          {/* Student Score */}
          <Radar
            name="Skor Siswa"
            dataKey="score"
            stroke="#3B82F6"
            fill="url(#radarGradient)"
            fillOpacity={0.4}
            strokeWidth={2.5}
            dot={{
              r: 5,
              fill: '#3B82F6',
              stroke: '#1E293B',
              strokeWidth: 2,
            }}
            activeDot={{
              r: 7,
              fill: '#60A5FA',
              stroke: '#fff',
              strokeWidth: 2,
            }}
          />

          {/* Tooltip */}
          <Tooltip
            contentStyle={{
              background: '#1E293B',
              border: '1px solid #334155',
              borderRadius: '12px',
              padding: '10px 14px',
              boxShadow: '0 10px 25px rgba(0,0,0,0.3)',
            }}
            labelStyle={{ color: '#F1F5F9', fontWeight: 600 }}
            itemStyle={{ color: '#94A3B8' }}
          />

          {/* Gradient definition */}
          <defs>
            <radialGradient id="radarGradient" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#3B82F6" stopOpacity={0.6} />
              <stop offset="100%" stopColor="#3B82F6" stopOpacity={0.1} />
            </radialGradient>
          </defs>
        </RechartsRadar>
      </ResponsiveContainer>
    </motion.div>
  );
}

export default RadarChart;
