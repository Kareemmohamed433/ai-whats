import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('khams_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem('khams_token') || null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      api.get('/auth/me')
        .then(res => {
          if (res.success) {
            setUser(res.user);
            localStorage.setItem('khams_user', JSON.stringify(res.user));
          }
        })
        .catch(() => {
          logout();
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = async (email, password) => {
    const res = await api.post('/auth/login', { email, password });
    if (res.success) {
      setToken(res.token);
      setUser(res.user);
      localStorage.setItem('khams_token', res.token);
      localStorage.setItem('khams_user', JSON.stringify(res.user));
      return res.user;
    }
    throw new Error(res.error?.message || 'فشل الدخول');
  };

  const logout = () => {
    if (token) {
      api.post('/auth/logout').catch(() => {});
    }
    setToken(null);
    setUser(null);
    localStorage.removeItem('khams_token');
    localStorage.removeItem('khams_user');
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
