/**
 * @module Sidebar
 * @desc Komponen navigasi sidebar dengan menu berbasis role.
 * @author Azhar Maulana
 * @date 25 Maret 2026
 * @version 1.0
 */

import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { motion } from 'framer-motion';

import { logout } from '../store/authSlice';
import { SIDEBAR_MENU, ROLES } from '../utils/constants';

/**
 * Komponen Sidebar navigasi dengan menu role-based.
 * @returns {JSX.Element} Sidebar.
 */
function Sidebar() {
  const { user } = useSelector((state) => state.auth);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  /**
   * Handler logout — hapus state dan redirect ke login.
   */
  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  // Filter menu berdasarkan role pengguna
  const visibleMenu = SIDEBAR_MENU.filter(
    (item) => item.roles.includes(user?.role)
  );

  return (
    <motion.aside
      initial={{ x: -280 }}
      animate={{ x: 0 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      className="w-64 h-screen bg-surface-800/80 backdrop-blur-lg border-r border-surface-700/50 flex flex-col"
    >
      {/* Logo */}
      <div className="p-6 border-b border-surface-700/50">
        <h2 className="text-xl font-display font-bold gradient-text">Zonara</h2>
        <p className="text-xs text-surface-200/40 mt-1">Character Analytics</p>
      </div>

      {/* User Info */}
      <div className="p-4 mx-3 mt-4 bg-surface-700/30 rounded-xl">
        <p className="text-sm font-medium text-white truncate">{user?.full_name}</p>
        <p className="text-xs text-surface-200/50 mt-1">
          {ROLES[user?.role]?.label || user?.role}
        </p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 mt-6 space-y-1">
        {visibleMenu.map((item) => (
          <NavLink
            key={item.key}
            to={item.path}
            className={({ isActive }) =>
              `nav-item pl-4 ${isActive ? 'nav-item-active' : ''}`
            }
          >
            <span className="text-sm">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-surface-700/50">
        <button
          onClick={handleLogout}
          className="nav-item w-full text-zona-red-400 hover:bg-zona-red-500/10"
        >
          <span className="text-sm">Keluar</span>
        </button>
      </div>
    </motion.aside>
  );
}

export default Sidebar;
