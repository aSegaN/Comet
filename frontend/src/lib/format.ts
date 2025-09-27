export const fmtDate = (iso?: string | null) =>
  iso ? new Date(iso).toLocaleString() : '—';
