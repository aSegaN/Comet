export const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

export async function api<T>(path: string): Promise<T> {
    const r = await fetch(`${API_BASE}${path}`);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json() as Promise<T>;
}