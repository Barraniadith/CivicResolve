import React from 'react';
import { StatsData } from '../types';

interface KPIProps {
  stats: StatsData | null;
  onRefresh: () => void;
}

export const KPIHeader: React.FC<KPIProps> = ({ stats, onRefresh }) => {
  return (
    <header className="bg-slate-900 border-b border-slate-800 px-6 py-4 flex flex-wrap items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400 font-bold text-xl shadow-inner">
          🏛️
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-white tracking-tight">CivicResolve</h1>
            <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-medium">
              Gemini 2.5 Flash
            </span>
          </div>
          <p className="text-xs text-slate-400">AI-Powered Citizen Grievance Redressal & Municipal Command</p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="bg-slate-800/80 border border-slate-700/60 rounded-lg px-4 py-1.5 text-center">
          <div className="text-xs text-slate-400">Total Grievances</div>
          <div className="text-lg font-bold text-white">{stats?.total_complaints ?? 0}</div>
        </div>
        <div className="bg-rose-950/40 border border-rose-800/50 rounded-lg px-4 py-1.5 text-center">
          <div className="text-xs text-rose-300">Critical Hazards</div>
          <div className="text-lg font-bold text-rose-400">{stats?.critical_count ?? 0}</div>
        </div>
        <div className="bg-amber-950/40 border border-amber-800/50 rounded-lg px-4 py-1.5 text-center">
          <div className="text-xs text-amber-300">In Progress</div>
          <div className="text-lg font-bold text-amber-400">{stats?.in_progress_count ?? 0}</div>
        </div>
        <div className="bg-emerald-950/40 border border-emerald-800/50 rounded-lg px-4 py-1.5 text-center">
          <div className="text-xs text-emerald-300">Resolved</div>
          <div className="text-lg font-bold text-emerald-400">{stats?.resolved_count ?? 0}</div>
        </div>
        <button
          onClick={onRefresh}
          className="p-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 hover:text-white transition"
          title="Refresh Data"
        >
          🔄
        </button>
      </div>
    </header>
  );
};
