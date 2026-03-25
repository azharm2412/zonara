/**
 * @module QRScanner
 * @desc Komponen camera QR scanner menggunakan html5-qrcode.
 *       Mengacu pada FR-003 (QR Scanner Decoder).
 *       
 *       Fix v1.1:
 *       - Stale closure pada cleanup → gunakan useRef untuk isScanning
 *       - Infinite re-render → pindahkan onScanResult ke useRef
 *       - Duplikat scan → debounce/cooldown 2 detik
 *       - Crash saat toggle → stop scanner sebelum restart
 *       - Tambah visual feedback scan berhasil
 *       - Error handling permission kamera
 *
 * @author Azhar Maulana
 * @date 25 Maret 2026
 * @version 1.1
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { Html5Qrcode } from 'html5-qrcode';

/** Durasi cooldown setelah scan berhasil (ms) */
const SCAN_COOLDOWN_MS = 2000;

/**
 * Komponen QR Scanner dengan dukungan kamera dan fallback manual.
 *
 * @param {object} props
 * @param {function} props.onScanResult - Callback saat QR berhasil dipindai.
 * @param {boolean} props.active - Status aktif scanner.
 * @returns {JSX.Element} QR Scanner.
 */
function QRScanner({ onScanResult, active = false }) {
  const scannerRef = useRef(null);
  const isScanningRef = useRef(false);
  const callbackRef = useRef(onScanResult);
  const lastScannedRef = useRef('');
  const cooldownTimerRef = useRef(null);

  const [manualInput, setManualInput] = useState('');
  const [scanFeedback, setScanFeedback] = useState(null); // { text, type }
  const [cameraError, setCameraError] = useState(null);

  // Selalu simpan callback terbaru tanpa masuk dependency array
  callbackRef.current = onScanResult;

  /**
   * Menghentikan scanner yang sedang berjalan.
   * @returns {Promise<void>}
   */
  const stopScanner = useCallback(async () => {
    if (scannerRef.current && isScanningRef.current) {
      try {
        await scannerRef.current.stop();
      } catch {
        // Ignore — scanner mungkin sudah berhenti
      }
      isScanningRef.current = false;
    }
  }, []);

  /**
   * Menampilkan feedback visual setelah scan berhasil.
   * @param {string} text - Teks feedback.
   * @param {'success'|'error'} type - Tipe feedback.
   */
  const showFeedback = useCallback((text, type = 'success') => {
    setScanFeedback({ text, type });
    setTimeout(() => setScanFeedback(null), SCAN_COOLDOWN_MS);
  }, []);

  /**
   * Handler QR decode dengan debounce/cooldown.
   * Mencegah duplikat scan dalam interval SCAN_COOLDOWN_MS.
   *
   * @param {string} decodedText - String QR yang terdeteksi kamera.
   */
  const handleDecode = useCallback((decodedText) => {
    // Skip jika QR sama masih dalam cooldown
    if (decodedText === lastScannedRef.current) return;

    // Set cooldown
    lastScannedRef.current = decodedText;
    if (cooldownTimerRef.current) clearTimeout(cooldownTimerRef.current);
    cooldownTimerRef.current = setTimeout(() => {
      lastScannedRef.current = '';
    }, SCAN_COOLDOWN_MS);

    // Kirim ke parent
    if (callbackRef.current) {
      callbackRef.current(decodedText);
      showFeedback(`✓ Terpindai: ${decodedText}`);
    }
  }, [showFeedback]);

  /**
   * Inisialisasi dan cleanup html5-qrcode scanner.
   * 
   * Fix: 
   * - Dependency hanya [active], bukan [active, onScanResult]
   * - isScanning disimpan di ref, bukan state
   * - Stop scanner lama sebelum memulai yang baru
   */
  useEffect(() => {
    if (!active) {
      // Jika dinonaktifkan, stop scanner yang sedang jalan
      stopScanner();
      return;
    }

    let mounted = true;
    setCameraError(null);

    const startScanner = async () => {
      // 1. Stop scanner lama jika masih jalan (fix double-camera bug)
      await stopScanner();

      // 2. Tunggu DOM element tersedia
      const element = document.getElementById('qr-reader');
      if (!element || !mounted) return;

      try {
        const html5QrCode = new Html5Qrcode('qr-reader');
        scannerRef.current = html5QrCode;

        await html5QrCode.start(
          { facingMode: 'environment' },
          {
            fps: 10,
            qrbox: { width: 250, height: 250 },
          },
          (decodedText) => {
            if (mounted) handleDecode(decodedText);
          },
          () => {
            // Frame tanpa QR — normal behavior, tidak perlu log
          }
        );

        if (mounted) {
          isScanningRef.current = true;
        }
      } catch (err) {
        console.error('QR Scanner start error:', err);
        if (mounted) {
          const errMsg = String(err);
          if (errMsg.includes('NotAllowedError') || errMsg.includes('Permission')) {
            setCameraError('Akses kamera ditolak. Izinkan akses kamera di pengaturan browser.');
          } else if (errMsg.includes('NotFoundError')) {
            setCameraError('Kamera tidak ditemukan. Gunakan input manual di bawah.');
          } else {
            setCameraError('Gagal membuka kamera. Gunakan input manual sebagai alternatif.');
          }
          isScanningRef.current = false;
        }
      }
    };

    // Delay sedikit agar DOM element `qr-reader` sudah ter-render
    const timer = setTimeout(startScanner, 100);

    // Cleanup: stop scanner saat unmount atau active berubah
    return () => {
      mounted = false;
      clearTimeout(timer);
      if (cooldownTimerRef.current) clearTimeout(cooldownTimerRef.current);

      // Stop scanner — gunakan ref (fix stale closure)
      if (scannerRef.current && isScanningRef.current) {
        scannerRef.current.stop().catch(() => {});
        isScanningRef.current = false;
      }
    };
  }, [active, handleDecode, stopScanner]);

  /**
   * Handler input manual sebagai fallback.
   */
  const handleManualSubmit = () => {
    const value = manualInput.trim();
    if (value && callbackRef.current) {
      callbackRef.current(value);
      showFeedback(`✓ Manual: ${value}`);
      setManualInput('');
    }
  };

  return (
    <div className="space-y-4">
      {/* Camera Viewfinder */}
      {active && (
        <div className="relative">
          <div
            id="qr-reader"
            className="w-full rounded-xl overflow-hidden border border-surface-600"
            style={{ minHeight: '250px' }}
          />

          {/* Scan Success Flash Overlay */}
          {scanFeedback && (
            <div
              className={`absolute inset-0 flex items-center justify-center rounded-xl transition-opacity duration-300 ${
                scanFeedback.type === 'success'
                  ? 'bg-zona-green-500/20 border-2 border-zona-green-400'
                  : 'bg-zona-red-500/20 border-2 border-zona-red-400'
              }`}
            >
              <span className={`text-lg font-bold ${
                scanFeedback.type === 'success' ? 'text-zona-green-400' : 'text-zona-red-400'
              }`}>
                {scanFeedback.text}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Camera Error Message */}
      {cameraError && (
        <div className="p-3 bg-zona-red-500/10 border border-zona-red-500/30 rounded-lg">
          <p className="text-sm text-zona-red-400">📷 {cameraError}</p>
        </div>
      )}

      {/* Manual Fallback Input (FR-003.5) */}
      <div>
        <label htmlFor="manual-qr-input" className="text-xs text-surface-200/50 block mb-1">
          Input Manual (Fallback)
        </label>
        <div className="flex gap-2">
          <input
            id="manual-qr-input"
            type="text"
            value={manualInput}
            onChange={(e) => setManualInput(e.target.value)}
            placeholder="Ketik kode QR (e.g., ZCA-B-001)"
            className="input-field flex-1 text-sm"
            onKeyDown={(e) => e.key === 'Enter' && handleManualSubmit()}
          />
          <button
            onClick={handleManualSubmit}
            disabled={!manualInput.trim()}
            className="btn-secondary text-sm px-4"
          >
            Kirim
          </button>
        </div>
      </div>
    </div>
  );
}

export default QRScanner;
