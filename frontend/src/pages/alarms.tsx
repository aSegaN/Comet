import React, { useMemo } from 'react';
import { useRouter } from 'next/router';
import { useAlarms } from '../hooks/useAlarms';
import type { Alarm } from '@/lib/types';
import { SeverityBadge } from '../components/SeverityBadge';
import { fmtDate } from '@/lib/format';

function useParamsFromUrl() {
  const router = useRouter();
  const sp = router.query;
  const page = sp.page ? parseInt(String(sp.page), 10) : 1;
  const page_size = sp.page_size ? parseInt(String(sp.page_size), 10) : 25;
  const severity = Array.isArray(sp.severity) ? sp.severity.map(String) :
                   sp.severity ? [String(sp.severity)] : undefined;
  const status = Array.isArray(sp.status) ? sp.status.map(String) :
                 sp.status ? [String(sp.status)] : undefined;
  const q = sp.q ? String(sp.q) : undefined;
  const ordering = sp.ordering ? String(sp.ordering) : '-started_at';
  return { page, page_size, severity, status, q, ordering };
}

export default function AlarmsPage() {
  const router = useRouter();
  const params = useParamsFromUrl();
  const { data, isLoading, isError, refetch } = useAlarms(params);

  const totals = useMemo(() => {
    const res = { total: data?.total ?? 0, CRITICAL: 0, MAJOR: 0, WARN: 0, INFO: 0 };
    (data?.items ?? []).forEach((a: Alarm) => { // comptage côté page (échantillon)
      (res as any)[a.severity] = ((res as any)[a.severity] ?? 0) + 1;
    });
    return res;
  }, [data]);

  const setParam = (k: string, v?: string | string[]) => {
    const next = new URLSearchParams(router.query as any);
    next.delete(k);
    if (Array.isArray(v)) v.forEach(x => next.append(k, x));
    else if (v) next.set(k, v);
    router.push({ pathname: '/alarms', query: next.toString() }, undefined, { shallow: true });
  };

  return (
    <div className="p-6 space-y-6">
      <header className="flex flex-wrap items-center gap-4">
        <h1 className="text-2xl font-bold">Alarmes</h1>
        <div className="ml-auto flex gap-2 text-sm">
          <span className="px-2 py-1 bg-red-100 text-red-800 rounded">CRITICAL: {totals.CRITICAL}</span>
          <span className="px-2 py-1 bg-orange-100 text-orange-800 rounded">MAJOR: {totals.MAJOR}</span>
          <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded">WARN: {totals.WARN}</span>
          <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded">INFO: {totals.INFO}</span>
          <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded">Total: {totals.total}</span>
        </div>
      </header>

      {/* Filtres */}
      <section className="flex flex-wrap items-center gap-3">
        <input
          placeholder="Rechercher (site/alarme)"
          defaultValue={params.q ?? ''}
          onKeyDown={(e) => { if (e.key === 'Enter') setParam('q', (e.target as HTMLInputElement).value || undefined) }}
          className="border rounded px-3 py-2"
        />
        <select
          value={params.severity?.[0] ?? ''}
          onChange={(e) => setParam('severity', e.target.value || undefined)}
          className="border rounded px-3 py-2"
        >
          <option value="">Sévérité (toutes)</option>
          <option value="CRITICAL">CRITICAL</option>
          <option value="MAJOR">MAJOR</option>
          <option value="WARN">WARN</option>
          <option value="INFO">INFO</option>
        </select>
        <select
          value={params.status?.[0] ?? ''}
          onChange={(e) => setParam('status', e.target.value || undefined)}
          className="border rounded px-3 py-2"
        >
          <option value="">Statut (tous)</option>
          <option value="OPEN">OPEN</option>
          <option value="CLEARED">CLEARED</option>
          <option value="ACK">ACK</option>
        </select>
        <select
          value={params.ordering}
          onChange={(e) => setParam('ordering', e.target.value)}
          className="border rounded px-3 py-2"
        >
          <option value="-started_at">Plus récent</option>
          <option value="started_at">Plus ancien</option>
          <option value="severity">Sévérité ↑</option>
          <option value="-severity">Sévérité ↓</option>
          <option value="site_name">Site A→Z</option>
          <option value="-site_name">Site Z→A</option>
        </select>
      </section>

      {/* Tableau */}
      <section className="overflow-x-auto">
        <table className="min-w-full border rounded">
          <thead className="bg-gray-50">
            <tr>
              <th className="p-2 text-left">Site</th>
              <th className="p-2 text-left">Alarme</th>
              <th className="p-2">Sévérité</th>
              <th className="p-2">Statut</th>
              <th className="p-2">Début</th>
              <th className="p-2">Fin</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && (
              <tr><td className="p-4" colSpan={6}>Chargement…</td></tr>
            )}
            {isError && (
              <tr><td className="p-4 text-red-600" colSpan={6}>Erreur de chargement</td></tr>
            )}
            {!isLoading && data?.items?.length === 0 && (
              <tr><td className="p-4" colSpan={6}>Aucune alarme</td></tr>
            )}
            {data?.items?.map((a: Alarm) => (
              <tr key={a.id} className="border-t">
                <td className="p-2">{a.site_name} <span className="text-xs text-gray-500">({a.site_id})</span></td>
                <td className="p-2">{a.alarm_label} <span className="text-xs text-gray-500">[{a.alarm_code}]</span></td>
                <td className="p-2 text-center"><SeverityBadge value={a.severity} /></td>
                <td className="p-2 text-center"><span className="text-xs">{a.status}</span></td>
                <td className="p-2">{fmtDate(a.started_at)}</td>
                <td className="p-2">{fmtDate(a.cleared_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {/* Pagination */}
      <footer className="flex items-center gap-3">
        <button
          disabled={(params.page ?? 1) <= 1}
          onClick={() => setParam('page', String((params.page ?? 1) - 1))}
          className="px-3 py-2 border rounded disabled:opacity-50"
        >
          ← Précédent
        </button>
        <span>Page {params.page ?? 1}</span>
        <button
          disabled={!!data && (params.page ?? 1) * (params.page_size ?? 25) >= data.total}
          onClick={() => setParam('page', String((params.page ?? 1) + 1))}
          className="px-3 py-2 border rounded disabled:opacity-50"
        >
          Suivant →
        </button>
        <select
          value={params.page_size}
          onChange={(e) => setParam('page_size', e.target.value)}
          className="border rounded px-2 py-1 ml-4"
        >
          {[10, 25, 50, 100, 200].map(n => <option key={n} value={n}>{n}/page</option>)}
        </select>
      </footer>
    </div>
  );
}
