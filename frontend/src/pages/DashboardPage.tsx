import { useDashboard } from '../api/hooks';
import { PageHeader } from '../components/ui/PageHeader';
import { StatCard } from '../components/ui/StatCard';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { AlertCircle, Wallet, ArrowRightLeft, Network } from 'lucide-react';

export default function DashboardPage() {
  const { data, isLoading, error } = useDashboard();

  if (isLoading) return <div className="space-y-4"><Skeleton className="h-10 w-48" /><div className="grid grid-cols-4 gap-4"><Skeleton className="h-24 w-full" /><Skeleton className="h-24 w-full" /><Skeleton className="h-24 w-full" /><Skeleton className="h-24 w-full" /></div></div>;
  if (error) return <ErrorState message="Failed to load dashboard data." />;

  return (
    <div className="space-y-6">
      <PageHeader title="Command Center" description="Overview of network intelligence" />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={<ArrowRightLeft />} label="Total Transactions" value={data?.stats?.totalTx || 0} />
        <StatCard icon={<Wallet />} label="Active Wallets" value={data?.stats?.activeWallets || 0} />
        <StatCard icon={<Network />} label="Monitored IPs" value={data?.stats?.monitoredIps || 0} />
        <StatCard icon={<AlertCircle />} label="Active Alerts" value={data?.stats?.activeAlerts || 0} />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
           <h3 className="text-lg font-medium mb-4">Anomaly Distribution</h3>
           <div className="h-64 flex items-center justify-center text-slate-500">Chart rendering...</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
           <h3 className="text-lg font-medium mb-4">System Health</h3>
           <div className="h-64 flex items-center justify-center text-slate-500">Health indicators...</div>
        </div>
      </div>
    </div>
  );
}
