import React from 'react';
import type { Severity } from '@/lib/types';

export function SeverityBadge({ value }: { value: Severity }) {
  const label = value;
  const styles: Record<Severity, string> = {
    INFO: 'bg-gray-200 text-gray-800',
    WARN: 'bg-yellow-200 text-yellow-900',
    MAJOR: 'bg-orange-200 text-orange-900',
    CRITICAL: 'bg-red-200 text-red-900',
  };
  return <span className={`px-2 py-1 rounded text-xs font-semibold ${styles[value]}`}>{label}</span>;
}
