export const formatBTC = (satoshis: number) => (satoshis / 100000000).toFixed(8) + ' BTC';
export const formatNumber = (n: number) => new Intl.NumberFormat().format(n);
export const formatDate = (iso: string) => new Date(iso).toLocaleDateString();
export const formatRelativeTime = (iso: string) => {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  return `${mins} mins ago`;
}
export const truncateAddress = (addr: string) => `${addr.slice(0, 6)}...${addr.slice(-4)}`;
export const getPriorityColor = (p: string) => {
  const map: Record<string, string> = { CRITICAL: 'bg-rose-500', HIGH: 'bg-amber-500', MEDIUM: 'bg-blue-500', LOW: 'bg-slate-500' };
  return map[p] || 'bg-slate-500';
}
export const getStatusColor = (s: string) => {
  const map: Record<string, string> = { NEW: 'bg-blue-500', REVIEWING: 'bg-amber-500', RESOLVED: 'bg-emerald-500', DISMISSED: 'bg-slate-500' };
  return map[s] || 'bg-slate-500';
}
export const getEntityTypeIcon = (_type: string) => null;
