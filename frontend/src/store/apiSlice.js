/**
 * @module ApiSlice
 * @desc RTK Query base API dengan JWT header injection dan centralized error handling.
 * @author Azhar Maulana
 * @date 25 Maret 2026
 * @version 1.0
 */

import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { logout, setCredentials } from './authSlice';
import { getToken } from '../utils/helpers';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

/**
 * Base query dengan injeksi JWT header Authorization.
 */
const baseQuery = fetchBaseQuery({
  baseUrl: API_BASE_URL,
  prepareHeaders: (headers) => {
    const token = getToken();
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
    return headers;
  },
});

/**
 * Base query wrapper dengan logika auto-refresh token.
 * Jika mendapat 401, coba refresh token sebelum logout.
 *
 * @param {object} args - Argumen fetch request.
 * @param {object} api - RTK Query API object.
 * @param {object} extraOptions - Opsi tambahan.
 * @returns {object} Hasil query.
 */
const baseQueryWithReauth = async (args, api, extraOptions) => {
  let result = await baseQuery(args, api, extraOptions);

  if (result?.error?.status === 401) {
    // Coba refresh token
    const refreshResult = await baseQuery(
      { url: '/auth/refresh', method: 'POST' },
      api,
      extraOptions
    );

    if (refreshResult?.data?.data?.access_token) {
      // Simpan token baru
      api.dispatch(setCredentials({
        accessToken: refreshResult.data.data.access_token,
      }));
      // Retry request awal
      result = await baseQuery(args, api, extraOptions);
    } else {
      // Refresh gagal — paksa logout
      api.dispatch(logout());
    }
  }

  return result;
};

/**
 * RTK Query API slice utama.
 * Seluruh endpoint API diinjeksikan dari file terpisah (endpoints).
 */
export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: baseQueryWithReauth,
  tagTypes: ['Students', 'Sessions', 'Analytics'],
  endpoints: (builder) => ({
    // === Auth ===
    login: builder.mutation({
      query: (credentials) => ({
        url: '/auth/login',
        method: 'POST',
        body: credentials,
      }),
    }),
    register: builder.mutation({
      query: (data) => ({
        url: '/auth/register',
        method: 'POST',
        body: data,
      }),
    }),

    // === Students ===
    getStudents: builder.query({
      query: (className) => ({
        url: '/students',
        params: className ? { class_name: className } : {},
      }),
      providesTags: ['Students'],
    }),
    createStudent: builder.mutation({
      query: (data) => ({
        url: '/students',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Students'],
    }),

    // === Sessions ===
    getSessions: builder.query({
      query: () => '/sessions',
      providesTags: ['Sessions'],
    }),
    createSession: builder.mutation({
      query: (data) => ({
        url: '/sessions',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Sessions'],
    }),
    endSession: builder.mutation({
      query: (sessionId) => ({
        url: `/sessions/${sessionId}/end`,
        method: 'PATCH',
      }),
      invalidatesTags: ['Sessions'],
    }),

    // === Scan & Score (2-step flow) ===
    lookupCard: builder.mutation({
      query: (data) => ({
        url: '/scan/lookup',
        method: 'POST',
        body: data,
      }),
    }),
    confirmScore: builder.mutation({
      query: (data) => ({
        url: '/scan/confirm',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Analytics'],
    }),
    // Legacy 1-step scan (backward compat)
    scanScore: builder.mutation({
      query: (data) => ({
        url: '/scan',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Analytics'],
    }),

    // === Session Players ===
    getSessionPlayers: builder.query({
      query: (sessionId) => `/sessions/${sessionId}/players`,
      providesTags: ['Sessions'],
    }),

    // === Analytics ===
    getRadarData: builder.query({
      query: (studentId) => `/analytics/radar/${studentId}`,
      providesTags: ['Analytics'],
    }),
    getClassSummary: builder.query({
      query: (className) => ({
        url: '/analytics/class-summary',
        params: { class_name: className },
      }),
      providesTags: ['Analytics'],
    }),
    getSessionRadar: builder.query({
      query: (sessionId) => `/analytics/session-radar/${sessionId}`,
      providesTags: ['Analytics'],
    }),
  }),
});

export const {
  useLoginMutation,
  useRegisterMutation,
  useGetStudentsQuery,
  useCreateStudentMutation,
  useGetSessionsQuery,
  useCreateSessionMutation,
  useEndSessionMutation,
  useLookupCardMutation,
  useConfirmScoreMutation,
  useScanScoreMutation,
  useGetSessionPlayersQuery,
  useGetRadarDataQuery,
  useGetClassSummaryQuery,
  useGetSessionRadarQuery,
} = apiSlice;

