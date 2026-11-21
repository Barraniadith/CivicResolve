import { Complaint, StatsData, AIPreviewResult } from './types';

const API_BASE = '/api';

export async function fetchStats(): Promise<StatsData> {
  const res = await fetch(`${API_BASE}/stats`);
  if (!res.ok) throw new Error('Failed to load stats');
  return res.json();
}

export async function fetchComplaints(params?: {
  status?: string;
  urgency?: string;
  department?: string;
  search?: string;
  limit?: number;
  offset?: number;
}): Promise<Complaint[]> {
  const query = new URLSearchParams();
  if (params?.status && params.status !== 'All') query.append('status', params.status);
  if (params?.urgency && params.urgency !== 'All') query.append('urgency', params.urgency);
  if (params?.department && params.department !== 'All') query.append('department', params.department);
  if (params?.search) query.append('search', params.search);
  if (params?.limit) query.append('limit', String(params.limit));
  if (params?.offset) query.append('offset', String(params.offset));

  const res = await fetch(`${API_BASE}/complaints?${query.toString()}`);
  if (!res.ok) throw new Error('Failed to load complaints');
  return res.json();
}

export async function previewAITriage(payload: {
  title?: string;
  description: string;
  location_name?: string;
  image_data_base64?: string;
}): Promise<AIPreviewResult> {
  const res = await fetch(`${API_BASE}/ai/preview`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('AI Triage failed');
  return res.json();
}

export async function createComplaint(payload: Partial<Complaint>): Promise<Complaint> {
  const res = await fetch(`${API_BASE}/complaints`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Failed to submit grievance');
  return res.json();
}

export async function updateComplaintStatus(
  id: string,
  status: string,
  officer?: string,
  notes?: string
): Promise<Complaint> {
  const res = await fetch(`${API_BASE}/complaints/${id}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      status,
      assigned_officer: officer,
      resolution_notes: notes
    })
  });
  if (!res.ok) throw new Error('Failed to update status');
  return res.json();
}
