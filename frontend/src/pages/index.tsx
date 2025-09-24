import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';


type Health = { status: string };
export default function Home() {
    const { data, isLoading } = useQuery({
        queryKey: ['health'],
        queryFn: () => api<Health>('/api/health'),
    });
    return (
        <main style={{ padding: 24 }}>
        <h1>Centre de supervision des alarmes</h1>
        <p>API health: {isLoading ? '…' : data?.status}</p>
        </main>
    );
}