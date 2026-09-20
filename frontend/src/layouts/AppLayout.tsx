import { useState, useRef, useEffect } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, AlertCircle, Wallet, ArrowRightLeft, Network, 
  Activity, Briefcase, Database, Cpu, ShieldAlert, Search, X, 
  ExternalLink, Clock, FileText, ChevronRight, GitMerge, ShieldCheck, Terminal, Settings
} from 'lucide-react';
import { useSearch, useSystemStatus } from '../api/hooks';
import { truncateAddress } from '../utils/format';

const navItems = [
  { name: 'Command Center', path: '/', icon: <LayoutDashboard size={18} /> },
  { name: 'Alert Prioritizer', path: '/alerts', icon: <AlertCircle size={18} /> },
  { name: 'Investigation Graph', path: '/graph', icon: <Network size={18} /> },
  { name: 'Structural Heuristics', path: '/heuristics', icon: <GitMerge size={18} /> },
  { name: 'Wallets', path: '/wallets', icon: <Wallet size={18} /> },
  { name: 'Transactions', path: '/transactions', icon: <ArrowRightLeft size={18} /> },
  { name: 'Cases & Reports', path: '/cases', icon: <Briefcase size={18} /> },
  { name: 'Dataset Management', path: '/datasets', icon: <Database size={18} /> },
  { name: 'Data Quality & Quarantine', path: '/data-quality', icon: <ShieldCheck size={18} /> },
  { name: 'Model Lab', path: '/models', icon: <Cpu size={18} /> },
  { name: 'Audit Trail', path: '/audit-logs', icon: <Terminal size={18} /> },
  { name: 'Settings & RBAC', path: '/settings', icon: <Settings size={18} /> },
  { name: 'System Status', path: '/system', icon: <Activity size={18} /> },
];

export default function AppLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);

  const { data: searchData, isLoading: isSearching } = useSearch(searchQuery);
  const { data: systemStatus } = useSystemStatus();

  // Close search dropdown on click outside
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) {
        setIsSearchOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearchResultClick = (url: string) => {
    setIsSearchOpen(false);
    setSearchQuery('');
    navigate(url);
  };

  return (
    <div className="flex h-screen overflow-hidden bg-slate-950 text-slate-100 font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900/95 border-r border-slate-800/80 flex flex-col shrink-0">
        {/* Brand */}
        <div className="p-4 border-b border-slate-800/80 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400">
              <ShieldAlert size={20} />
            </div>
            <div>
              <div className="font-bold tracking-tight text-white flex items-center gap-1.5">
                BTC-SHIELD
                <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
                  NTRO
                </span>
              </div>
              <div className="text-[11px] text-slate-400 truncate max-w-[140px]">
                Network & TX Intel
              </div>
            </div>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          <div className="px-3 pb-2 text-[10px] font-mono tracking-wider text-slate-400 uppercase">
            Platform Modules
          </div>
          {navItems.map((item) => {
            const isActive = location.pathname === item.path || 
              (item.path !== '/' && location.pathname.startsWith(item.path));
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <span className={isActive ? 'text-blue-400' : 'text-slate-400'}>
                  {item.icon}
                </span>
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* System & Team Footer */}
        <div className="p-3 border-t border-slate-800/80 bg-slate-950/40">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span className="flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full ${systemStatus?.database === 'OPERATIONAL' ? 'bg-emerald-500' : 'bg-amber-500'} animate-pulse`} />
              System Status
            </span>
            <span className="font-mono text-[11px] text-emerald-400">
              {systemStatus?.database === 'OPERATIONAL' ? 'ONLINE' : 'ACTIVE'}
            </span>
          </div>
          <div className="text-[11px] text-slate-400 text-center font-mono">
            SIH 2026 • Problem 26146
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Top Header */}
        <header className="h-16 bg-slate-900/80 backdrop-blur border-b border-slate-800/80 flex items-center justify-between px-6 shrink-0 z-20">
          {/* Global Search */}
          <div className="relative w-full max-w-lg" ref={searchRef}>
            <div className="relative">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setIsSearchOpen(true);
                }}
                onFocus={() => setIsSearchOpen(true)}
                placeholder="Search wallet, TXID, IP, ASN, alert, or case..."
                className="w-full pl-10 pr-9 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-slate-200 placeholder-slate-400 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/30"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-300"
                >
                  <X size={14} />
                </button>
              )}
            </div>

            {/* Search Dropdown Results */}
            {isSearchOpen && searchQuery.length >= 2 && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-slate-900 border border-slate-800 rounded-lg shadow-2xl overflow-hidden max-h-96 z-50">
                {isSearching ? (
                  <div className="p-4 text-xs text-slate-400 text-center">Searching intelligence entities...</div>
                ) : searchData?.results && searchData.results.length > 0 ? (
                  <div className="divide-y divide-slate-800/60 overflow-y-auto max-h-80">
                    {searchData.results.map((r: any, idx: number) => (
                      <button
                        key={idx}
                        onClick={() => handleSearchResultClick(r.url)}
                        className="w-full px-4 py-2.5 text-left flex items-center justify-between hover:bg-slate-800/50 transition-colors"
                      >
                        <div className="truncate pr-4">
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                              {r.type}
                            </span>
                            <span className="text-sm font-medium text-white truncate">
                              {r.type === 'WALLET' ? truncateAddress(r.label) : r.label}
                            </span>
                          </div>
                          <div className="text-xs text-slate-400 truncate mt-0.5">{r.subtitle}</div>
                        </div>
                        <ChevronRight size={14} className="text-slate-400 shrink-0" />
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="p-4 text-xs text-slate-400 text-center">
                    No entities found matching "{searchQuery}"
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Right Profile & Info */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-xs font-mono px-3 py-1.5 rounded-md bg-slate-800/50 border border-slate-700/50 text-slate-300">
              <span className="w-2 h-2 rounded-full bg-blue-400" />
              <span>INVESTIGATOR (ADMIN)</span>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-6 relative">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
