export type Severity = 'INFO' | 'WARN' | 'MAJOR' | 'CRITICAL';
export type Status = 'OPEN' | 'CLEARED' | 'ACK';

export interface Alarm {
  id: number;
  site_id: string;
  site_name: string;
  alarm_code: string;
  alarm_label: string;
  severity: Severity;
  status: Status;
  started_at: string;
  cleared_at?: string | null;
  acked_at?: string | null;
}

export interface AlarmListResponse {
  items: Alarm[];
  page: number;
  page_size: number;
  total: number;
}
