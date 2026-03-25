/**
 * @module TailwindConfig
 * @desc Konfigurasi Tailwind CSS v3 dengan palet warna Zonara.
 *       Zona Biru (#3B82F6), Hijau (#22C55E), Kuning (#F59E0B), Merah (#EF4444).
 * @author Azhar Maulana
 * @date 25 Maret 2026
 * @version 1.0
 */

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Palet Warna Zonara — 4 Zona Karakter CASEL
        'zona-blue': {
          DEFAULT: '#3B82F6',
          50: '#EBF2FE',
          100: '#D7E6FD',
          200: '#AFCCFB',
          300: '#87B3F9',
          400: '#5F99F7',
          500: '#3B82F6',
          600: '#0B61EE',
          700: '#084AB7',
          800: '#063480',
          900: '#031D49',
        },
        'zona-green': {
          DEFAULT: '#22C55E',
          50: '#EAFBF0',
          100: '#D5F6E1',
          200: '#ABEEC4',
          300: '#82E5A6',
          400: '#58DD89',
          500: '#22C55E',
          600: '#1A9A49',
          700: '#136F35',
          800: '#0D4520',
          900: '#061A0C',
        },
        'zona-yellow': {
          DEFAULT: '#F59E0B',
          50: '#FEF6E7',
          100: '#FDEDD0',
          200: '#FBDBA1',
          300: '#F9C972',
          400: '#F7B743',
          500: '#F59E0B',
          600: '#C47F09',
          700: '#935F06',
          800: '#623F04',
          900: '#312002',
        },
        'zona-red': {
          DEFAULT: '#EF4444',
          50: '#FDECEC',
          100: '#FCD9D9',
          200: '#F9B3B3',
          300: '#F58D8D',
          400: '#F26767',
          500: '#EF4444',
          600: '#E71414',
          700: '#B30F0F',
          800: '#7F0B0B',
          900: '#4B0606',
        },
        // Aksen Emas (untuk badge/prestasi)
        'zona-gold': {
          DEFAULT: '#D4AF37',
          50: '#F9F3E1',
          500: '#D4AF37',
          700: '#A68B2C',
        },
        // Warna UI dasar
        'surface': {
         DEFAULT: '#0F172A',
          50: '#F8FAFC',  // Text Primary
          100: '#F1F5F9',
          200: '#E2E8F0',
          400: '#94A3B8', // Text Secondary
          500: '#64748B', // Text Muted
          600: '#475569', // Border (Kunci yang hilang penyebab error)
          700: '#334155', // Background Tertiary
          800: '#1E293B', // Background Secondary
          900: '#0F172A', // Background Primary
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        display: ['Outfit', 'Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'radar-pulse': 'radarPulse 2s ease-in-out infinite',
        'slide-up': 'slideUp 0.3s ease-out',
        'fade-in': 'fadeIn 0.4s ease-out',
      },
      keyframes: {
        radarPulse: {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.8', transform: 'scale(1.02)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};
