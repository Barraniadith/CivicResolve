import React, { useEffect, useState } from 'react';
import { Complaint, StatsData } from './types';
import { fetchComplaints, fetchStats } from './api';
import { KPIHeader } from './components/KPIHeader';
import { CitizenPortal } from './components/CitizenPortal';
import { AdminConsole } from './components/AdminConsole';

export const App: React.FC = () => {
  const [stats, setStats] = useState<StatsData | null>(null);
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const [s, c] = await Promise.all([fetchStats(), fetchComplaints({ limit: 100 })]);
      setStats(s);
      setComplaints(c);
    } catch (err) {
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <KPIHeader stats={stats} onRefresh={loadData} />

      <main className="flex-1 p-6 grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-7xl w-full mx-auto">
        <div className="h-full">
          <CitizenPortal onSubmitted={loadData} />
        </div>
        <div className="h-full">
          <AdminConsole complaints={complaints} onUpdated={loadData} />
        </div>
      </main>

      <footer className="py-3 text-center border-t border-slate-900 text-xs text-slate-500">
        CivicResolve • PromptWars GDG on-Campus PSG iTech • Powered by Google Gemini 2.5 Flash
      </footer>
    </div>
  );
};

export default App;
