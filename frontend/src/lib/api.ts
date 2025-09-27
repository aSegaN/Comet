const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

export interface ListParams {
  page?: number;
  page_size?: number;
  severity?: string[]; // ex ['CRITICAL','WARN']
  status?: string[];
  q?: string;
  from?: string; // ISO
  to?: string;   // ISO
  ordering?: string; // '-started_at'
}

export async function fetchAlarms(params: ListParams = {}) {
  const u = new URL('/api/alarms', API_BASE);
  const entries: [string, string][] = [];

  if (params.page) entries.push(['page', String(params.page)]);
  if (params.page_size) entries.push(['page_size', String(params.page_size)]);
  if (params.severity) params.severity.forEach(s => entries.push(['severity', s]));
  if (params.status) params.status.forEach(s => entries.push(['status', s]));
  if (params.q) entries.push(['q', params.q]);
  if (params.from) entries.push(['from', params.from]);
  if (params.to) entries.push(['to', params.to]);
  if (params.ordering) entries.push(['ordering', params.ordering]);

  u.search = new URLSearchParams(entries).toString();

  const r = await fetch(u.toString(), { headers: { 'Accept': 'application/json' } });
  if (!r.ok) throw new Error(`API error ${r.status}`);
  return r.json();
}
