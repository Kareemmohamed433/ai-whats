import React, { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import TopBar from './TopBar';

export default function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const isInbox = location.pathname.startsWith('/inbox');

  return (
    <div className="flex h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 overflow-hidden">
      {/* Mobile backdrop */}
      {sidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 z-40 bg-slate-900/60 backdrop-blur-xs lg:hidden"
        />
      )}

      <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />

      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <TopBar toggleSidebar={() => setSidebarOpen(!sidebarOpen)} />

        {isInbox ? (
          <main className="flex-1 flex flex-col min-w-0 overflow-hidden p-0 md:p-4 bg-slate-50/50 dark:bg-slate-950/50">
            <div className="flex-1 flex flex-col min-w-0 h-full">
              <Outlet />
            </div>
          </main>
        ) : (
          <main className="flex-1 overflow-y-auto p-3 sm:p-4 md:p-6 bg-slate-50/50 dark:bg-slate-950/50">
            <div className="max-w-7xl mx-auto space-y-6">
              <Outlet />
            </div>
          </main>
        )}
      </div>
    </div>
  );
}
