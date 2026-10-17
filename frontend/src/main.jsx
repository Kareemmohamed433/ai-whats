import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import App from './App';
import './index.css';
import { notificationService } from './services/notificationService';

// Initialize Service Worker for PWA & Web Push
// (sw.js ignores Vite dev files, so it is safe to register in development too)
notificationService.registerServiceWorker();

class ErrorBoundary extends React.Component {
  state = { error: null };

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error('UI crash:', error, info.componentStack);
  }

  render() {
    if (this.state.error) {
      return (
        <div
          dir="ltr"
          style={{
            padding: 24,
            color: '#fb7185',
            background: '#0f172a',
            minHeight: '100vh',
            fontFamily: 'monospace',
            fontSize: 13,
            whiteSpace: 'pre-wrap'
          }}
        >
          {String(this.state.error?.stack || this.state.error)}
        </div>
      );
    }
    return this.props.children;
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <BrowserRouter>
        <AuthProvider>
          <ThemeProvider>
            <App />
          </ThemeProvider>
        </AuthProvider>
      </BrowserRouter>
    </ErrorBoundary>
  </React.StrictMode>
);