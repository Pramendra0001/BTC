export const formatBTC = (satoshis?: number) => {
  if (satoshis === undefined || satoshis === null) return '0.00000000 BTC';
  return (satoshis / 100000000).toLocaleString(undefined, { minimumFractionDigits: 8, maximumFractionDigits: 8 }) + ' BTC';
};

export const formatSatoshis = (satoshis?: number) => {
  if (satoshis === undefined || satoshis === null) return '0 sat';
  return new Intl.NumberFormat().format(Math.round(satoshis)) + ' sat';
};

export const formatNumber = (n?: number) => {
  if (n === undefined || n === null) return '0';
  return new Intl.NumberFormat().format(n);
};

export const formatDate = (iso?: string) => {
  if (!iso) return 'N/A';
  try {
    const d = new Date(iso);
    return isNaN(d.getTime()) ? 'N/A' : d.toLocaleString();
  } catch {
    return 'N/A';
  }
};

export const formatRelativeTime = (iso?: string) => {
  if (!iso) return 'N/A';
  try {
    const diff = Date.now() - new Date(iso).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'just now';
    if (mins < 60) return `${mins}m ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  } catch {
    return 'N/A';
  }
};

export const truncateAddress = (addr?: string, front: number = 8, back: number = 6) => {
  if (!addr) return '';
  if (addr.length <= front + back) return addr;
  return `${addr.slice(0, front)}...${addr.slice(-back)}`;
};

export const getPriorityColor = (p?: string) => {
  const map: Record<string, { bg: string; text: string; border: string }> = {
    CRITICAL: { bg: 'bg-rose-500/10', text: 'text-rose-400', border: 'border-rose-500/30' },
    HIGH: { bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/30' },
    MEDIUM: { bg: 'bg-blue-500/10', text: 'text-blue-400', border: 'border-blue-500/30' },
    LOW: { bg: 'bg-slate-500/10', text: 'text-slate-400', border: 'border-slate-500/30' }
  };
  return map[p?.toUpperCase() || ''] || map.LOW;
};

export const getStatusColor = (s?: string) => {
  const map: Record<string, { bg: string; text: string; border: string }> = {
    NEW: { bg: 'bg-blue-500/10', text: 'text-blue-400', border: 'border-blue-500/30' },
    REVIEWING: { bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/30' },
    RESOLVED: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/30' },
    DISMISSED: { bg: 'bg-slate-500/10', text: 'text-slate-400', border: 'border-slate-500/30' },
    OPEN: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/30' },
    ACTIVE: { bg: 'bg-blue-500/10', text: 'text-blue-400', border: 'border-blue-500/30' },
    CLOSED: { bg: 'bg-slate-500/10', text: 'text-slate-400', border: 'border-slate-500/30' }
  };
  return map[s?.toUpperCase() || ''] || { bg: 'bg-slate-500/10', text: 'text-slate-400', border: 'border-slate-500/30' };
};
