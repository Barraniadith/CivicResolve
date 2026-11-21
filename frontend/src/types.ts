export interface AuditLog {
  id: number;
  complaint_id: string;
  action: string;
  actor: string;
  details?: string;
  timestamp: string;
}

export interface Complaint {
  id: string;
  title: string;
  description: string;
  location_name: string;
  latitude?: number;
  longitude?: number;
  image_url?: string;
  citizen_name?: string;
  citizen_phone?: string;
  category: string;
  urgency: 'Critical' | 'High' | 'Medium' | 'Low';
  public_impact_score: number;
  department: string;
  ai_confidence: number;
  ai_reasoning?: string;
  status: 'Reported' | 'In Progress' | 'Resolved';
  assigned_officer?: string;
  resolution_notes?: string;
  resolution_image_url?: string;
  created_at: string;
  updated_at: string;
  logs: AuditLog[];
}

export interface AIPreviewResult {
  category: string;
  urgency: 'Critical' | 'High' | 'Medium' | 'Low';
  public_impact_score: number;
  department: string;
  confidence: number;
  reasoning: string;
  suggested_title?: string;
  hazard_flags: string[];
  is_fallback: boolean;
}

export interface StatsData {
  total_complaints: number;
  reported_count: number;
  in_progress_count: number;
  resolved_count: number;
  critical_count: number;
  high_count: number;
  department_breakdown: Record<string, number>;
  category_breakdown: Record<string, number>;
}
