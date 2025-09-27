import { useQuery } from '@tanstack/react-query';
import { fetchAlarms, ListParams } from '@/lib/api';

export function useAlarms(params: ListParams) {
  return useQuery({
    queryKey: ['alarms', params],
    queryFn: () => fetchAlarms(params),
    staleTime: 10_000,
    keepPreviousData: true,
  });
}
