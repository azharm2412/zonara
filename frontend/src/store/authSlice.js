/**
 * @module AuthSlice
 * @desc Redux slice untuk state management autentikasi (user, tokens, login/logout).
 * @author Azhar Maulana
 * @date 25 Maret 2026
 * @version 1.0
 */

import { createSlice } from '@reduxjs/toolkit';
import { getToken, getUser, saveAuth, clearAuth } from '../utils/helpers';

/**
 * State awal: cek localStorage untuk persisted session.
 */
const initialState = {
  user: getUser(),
  accessToken: getToken(),
  isAuthenticated: !!getToken(),
};

/**
 * Auth slice — mengelola state autentikasi global.
 */
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    /**
     * Set kredensial setelah login berhasil.
     * @param {object} state - State Redux.
     * @param {object} action - Payload: { user, accessToken, refreshToken }.
     */
    setCredentials: (state, action) => {
      const { user, accessToken, refreshToken } = action.payload;
      if (user) state.user = user;
      if (accessToken) state.accessToken = accessToken;
      state.isAuthenticated = true;
      saveAuth({ user: user || state.user, accessToken, refreshToken });
    },

    /**
     * Logout — hapus seluruh state dan localStorage.
     * @param {object} state - State Redux.
     */
    logout: (state) => {
      state.user = null;
      state.accessToken = null;
      state.isAuthenticated = false;
      clearAuth();
    },
  },
});

export const { setCredentials, logout } = authSlice.actions;
export default authSlice.reducer;
