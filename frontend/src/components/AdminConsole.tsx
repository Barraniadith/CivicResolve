import React from 'react';
import { Complaint } from '../types';
import { updateComplaintStatus } from '../api';

interface AdminProps {
  complaints: Complaint[];
  onUpdated: () => void;
}

export const AdminConsole: React.FC<AdminProps> = ({ complaints, onUpdated }) => {
  const handleStatusChange = async (id: string, newStatus: string) => {
    await updateComplaintStatus(id, newStatus, 'Municipal Duty Officer', `Status transitioned to ${newStatus}`);
    onUpdated();
  };

  return (
    <section className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col h-full overflow-hidden">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <span>🏢</span> Municipal Command Center
        </h2>
        <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
          Live Dispatch Queue
        </span>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
        {complaints.length === 0 ? (
          <div className="text-center py-10 text-slate-500 text-xs">No active grievances in this queue.</div>
        ) : (
          complaints.map((c) => (
            <div
              key={c.id}
              className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 hover:border-slate-700 transition space-y-2.5"
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] font-mono text-blue-400 bg-blue-950/40 px-1.5 py-0.5 rounded border border-blue-900/50">
                      {c.id}
                    </span>
                    <h3 className="text-sm font-semibold text-white">{c.title}</h3>
                  </div>
                  <div className="text-xs text-slate-400 mt-0.5">📍 {c.location_name}</div>
                </div>

                <span
                  className={`text-[11px] font-bold px-2 py-0.5 rounded ${
                    c.urgency === 'Critical'
                      ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                      : c.urgency === 'High'
                      ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                      : 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                  }`}
                >
                  {c.urgency}
                </span>
              </div>

              <p className="text-xs text-slate-300 line-clamp-2">{c.description}</p>

              <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-900 text-xs">
                <span className="text-[11px] text-slate-400 font-medium">
                  🏛️ {c.department.split('-')[0]}
                </span>

                <div className="flex items-center gap-2">
                  <select
                    value={c.status}
                    onChange={(e) => handleStatusChange(c.id, e.target.value)}
                    className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded px-2 py-1 focus:outline-none focus:border-blue-500"
                  >
                    <option value="Reported">Reported</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Resolved">Resolved</option>
                  </select>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </section>
  );
};
