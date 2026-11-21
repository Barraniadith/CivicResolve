import React, { useState } from 'react';
import { AIPreviewResult } from '../types';
import { previewAITriage, createComplaint } from '../api';

const PRESETS = [
  {
    title: 'Snapped Live Electric Wire at Neelambur Bypass',
    desc: 'High voltage electrical wire sparking openly near the bus stop pedestrian lane.',
    loc: 'Neelambur Bypass'
  },
  {
    title: 'Massive Crater Pothole on Avinashi Road',
    desc: 'Deep asphalt crater causing two-wheelers to swerve dangerously into ongoing bus traffic.',
    loc: 'Avinashi Road, Peelamedu'
  },
  {
    title: 'Overflowing Garbage Bin near PSG iTech Entrance',
    desc: 'Waste dump uncleared for four days emitting toxic foul smell and attracting strays.',
    loc: 'PSG iTech Campus Gate'
  }
];

export const CitizenPortal: React.FC<{ onSubmitted: () => void }> = ({ onSubmitted }) => {
  const [title, setTitle] = useState('');
  const [desc, setDesc] = useState('');
  const [loc, setLoc] = useState('Coimbatore');
  const [preview, setPreview] = useState<AIPreviewResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleRunAI = async () => {
    if (!desc.trim()) return;
    setLoading(true);
    try {
      const res = await previewAITriage({ title, description: desc, location_name: loc });
      setPreview(res);
      if (!title && res.suggested_title) setTitle(res.suggested_title);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!desc.trim()) return;
    setSubmitting(true);
    try {
      await createComplaint({
        title: title || 'Civic Grievance',
        description: desc,
        location_name: loc,
        category: preview?.category || 'Other Civic Grievance',
        urgency: preview?.urgency || 'Medium',
        department: preview?.department || 'CCMC - Public Grievance Redressal Cell'
      });
      setTitle('');
      setDesc('');
      setPreview(null);
      onSubmitted();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col h-full">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <span>📱</span> Citizen Grievance Portal
        </h2>
        <span className="text-xs text-slate-400">Mobile-First Intake</span>
      </div>

      <div className="mb-4">
        <div className="text-xs text-slate-400 mb-1.5 font-medium">Quick Demo Presets:</div>
        <div className="flex flex-wrap gap-2">
          {PRESETS.map((p, i) => (
            <button
              key={i}
              type="button"
              onClick={() => {
                setTitle(p.title);
                setDesc(p.desc);
                setLoc(p.loc);
              }}
              className="text-xs px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-blue-400 border border-slate-700/80 transition"
            >
              {p.title.split(' ')[0]} {p.title.split(' ')[1]}
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-3.5 flex-1 flex flex-col justify-between">
        <div className="space-y-3">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Issue Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Broken streetlight causing dark alley"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Description *</label>
            <textarea
              rows={3}
              required
              value={desc}
              onChange={(e) => setDesc(e.target.value)}
              placeholder="Describe the defect, hazards, or immediate risks..."
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Landmark / Location</label>
            <input
              type="text"
              value={loc}
              onChange={(e) => setLoc(e.target.value)}
              placeholder="e.g. Neelambur, Avinashi Road"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
            />
          </div>

          <button
            type="button"
            onClick={handleRunAI}
            disabled={loading || !desc.trim()}
            className="w-full py-2 px-3 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-md transition disabled:opacity-50"
          >
            {loading ? 'Analyzing with Gemini...' : '✨ Analyze with Google Gemini AI'}
          </button>

          {preview && (
            <div className="p-3 rounded-xl bg-slate-950 border border-blue-500/30 text-xs space-y-1.5 animate-fadeIn">
              <div className="flex justify-between items-center">
                <span className="font-semibold text-blue-400">{preview.category}</span>
                <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                  preview.urgency === 'Critical' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40' :
                  preview.urgency === 'High' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40' :
                  'bg-blue-500/20 text-blue-400'
                }`}>
                  {preview.urgency} Priority ({preview.public_impact_score}/5)
                </span>
              </div>
              <div className="text-slate-300">🏢 Routes to: <span className="text-white font-medium">{preview.department}</span></div>
              <div className="text-slate-400 italic text-[11px]">{preview.reasoning}</div>
            </div>
          )}
        </div>

        <button
          type="submit"
          disabled={submitting || !desc.trim()}
          className="w-full py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm shadow-lg transition disabled:opacity-50 mt-2"
        >
          {submitting ? 'Submitting...' : '🚀 Submit Grievance'}
        </button>
      </form>
    </section>
  );
};
