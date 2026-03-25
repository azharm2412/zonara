/**
 * @module Store
 * @desc Konfigurasi Redux store dengan RTK Query middleware.
 * @author Azhar Maulana
 * @date 25 Maret 2026
 * @version 1.0
 */

import { configureStore } from '@reduxjs/toolkit';
import { apiSlice } from './apiSlice';
import authReducer from './authSlice';

/**
 * Redux store utama aplikasi Zonara.
 * Menggabungkan auth state, RTK Query cache, dan middleware.
 */
export const store = configureStore({
  reducer: {
    auth: authReducer,
    [apiSlice.reducerPath]: apiSlice.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(apiSlice.middleware),
  devTools: import.meta.env.DEV,
});
