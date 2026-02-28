import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types matching backend schemas
export interface GraphNode {
  id: string;
  type: 'person' | 'task' | 'pr' | 'message' | 'channel';
  label: string;
  metadata: Record<string, unknown>;
  activity_level: number;
  color?: string;
  size?: number;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relationship: string;
  weight: number;
  animated: boolean;
  metadata: Record<string, unknown>;
}

export interface WorkGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
  last_updated: string;
}

export interface ToolPulse {
  name: string;
  status: 'active' | 'inactive' | 'error';
  metric: string;
  metric_value: number;
}

export interface PulseStatus {
  github: ToolPulse;
  jira: ToolPulse;
  slack: ToolPulse;
  last_sync: string;
}

export interface Bottleneck {
  task_id: string;
  task_title: string;
  pr_id?: string;
  pr_status?: string;
  last_slack_activity?: string;
  hours_since_activity: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
}

export interface OverloadScore {
  person_id: string;
  person_name: string;
  task_count: number;
  activity_count: number;
  overload_ratio: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
}

export interface RiskItem {
  pr_id: string;
  pr_title: string;
  ticket_id?: string;
  ticket_status?: string;
  risk_type: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

export interface ShadowTask {
  thread_id: string;
  channel: string;
  message_count: number;
  participants: string[];
  first_message: string;
  last_message: string;
  sample_text: string;
  suggested_ticket_title: string;
}

export interface InsightsReport {
  bottlenecks: Bottleneck[];
  overload_scores: OverloadScore[];
  risks: RiskItem[];
  shadow_tasks: ShadowTask[];
  generated_at: string;
}

export interface ChatResponse {
  response: string;
  sources: string[];
  confidence: number;
  related_nodes: string[];
}

export interface ActivityBrief {
  summary: string;
  key_updates: string[];
  hot_threads: number;
  blocked_tasks: number;
  merged_prs: number;
  period_start: string;
  period_end: string;
}

// API functions
export const getWorkGraph = async (refresh = false): Promise<WorkGraph> => {
  const response = await api.get('/graph', { params: { refresh } });
  return response.data;
};

export const getPulseStatus = async (): Promise<PulseStatus> => {
  const response = await api.get('/pulse');
  return response.data;
};

export const getInsights = async (): Promise<InsightsReport> => {
  const response = await api.get('/insights');
  return response.data;
};

export const getActivityBrief = async (): Promise<ActivityBrief> => {
  const response = await api.get('/insights/brief');
  return response.data;
};

export const chatWithGraph = async (query: string): Promise<ChatResponse> => {
  const response = await api.post('/chat', { query });
  return response.data;
};

export const regenerateData = async (): Promise<void> => {
  await api.post('/data/regenerate');
};

export const searchGraph = async (query: string): Promise<{ results: GraphNode[]; count: number }> => {
  const response = await api.get('/graph/search', { params: { query } });
  return response.data;
};

export default api;
