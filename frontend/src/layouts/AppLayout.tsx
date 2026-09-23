import { useState, useRef, useEffect, Suspense } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, AlertCircle, Wallet, ArrowRightLeft, Network, 
  Activity, Briefcase, Database, Cpu, ShieldAlert, Search, X, 
  ChevronRight, GitMerge, ShieldCheck, Terminal, Settings, Menu, LogOut, User as UserIcon
} from 'lucide-react';
import { useSearch, useSystemStatus } from '../api/hooks';
import { truncateAddress } from '../utils/format';
import { ThemeToggle } from '../components/ui/ThemeToggle';
import { useTheme } from '../context/ThemeContext';
import shieldLight from '../assets/shield-light.png';
import shieldDark from '../assets/shield-dark.png';

const navItems = [
  { name: 'Command Center', path: '/', icon: <LayoutDashboard size={17} /> },
  { name: 'Alert Prioritizer', path: '/alerts', icon: <AlertCircle size={17} /> },
  { name: 'Investigation Graph', path: '/graph', icon: <Network size={17} /> },
  { name: 'Structural Heuristics', path: '/heuristics', icon: <GitMerge size={17} /> },
  { name: 'Wallets', path: '/wallets', icon: <Wallet size={17} /> },
  { name: 'Transactions', path: '/transactions', icon: <ArrowRightLeft size={17} /> },
  { name: 'Cases & Reports', path: '/cases', icon: <Briefcase size={17} /> },
  { name: 'Dataset Management', path: '/datasets', icon: <Database size={17} /> },
  { name: 'Data Quality & Quarantine', path: '/data-quality', icon: <ShieldCheck size={17} /> },
  { name: 'Model Lab', path: '/models', icon: <Cpu size={17} /> },
  { name: 'Audit Trail', path: '/audit-logs', icon: <Terminal size={17} /> },
  { name: 'Settings & RBAC', path: '/settings', icon: <Settings size={17} /> },
  { name: 'System Status', path: '/system', icon: <Activity size={17} /> },
];

export default function AppLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);

  const { data: searchData, isLoading: isSearching } = useSearch(searchQuery);
  const { data: systemStatus } = useSystemStatus();
  const { resolvedTheme } = useTheme();
  const shieldLogo = resolvedTheme === 'dark' ? shieldDark : shieldLight;

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

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  const handleSearchResultClick = (url: string) => {
    setIsSearchOpen(false);
    setSearchQuery('');
    navigate(url);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <div className="flex h-screen overflow-hidden bg-slate-950 text-slate-100 font-sans">
      {/* Mobile Drawer Backdrop */}
      {mobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/60 z-40 lg:hidden backdrop-blur-xs"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-slate-900 border-r border-slate-800 flex flex-col shrink-0 transition-transform duration-200 ease-in-out
        lg:static lg:translate-x-0
        ${mobileMenuOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full'}
      `}>
        {/* Brand Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5">
            <img 
              src={shieldLogo} 
              alt="BTC-SHIELD" 
              className="w-8 h-8 object-contain shrink-0" 
            />
            <div>
              <div className="font-bold text-sm tracking-tight text-white font-mono">
                BTC-SHIELD
              </div>
              <div className="text-[10px] text-slate-400">
                Forensic Intelligence Platform
              </div>
            </div>
          </Link>
          <button
            onClick={() => setMobileMenuOpen(false)}
            className="lg:hidden p-1 text-slate-400 hover:text-slate-200"
            aria-label="Close navigation"
          >
            <X size={18} />
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 overflow-y-auto px-2.5 py-3 space-y-0.5">
          <div className="px-3 py-1.5 text-[10px] font-mono tracking-wider text-slate-500 uppercase">
            Investigation Modules
          </div>
          {navItems.map((item) => {
            const isActive = location.pathname === item.path || 
              (item.path !== '/' && location.pathname.startsWith(item.path));
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-2.5 px-3 py-2 rounded text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-slate-800 text-slate-100 font-semibold border-l-2 border-blue-500 pl-2.5'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-850/60'
                }`}
              >
                <span className={isActive ? 'text-blue-400' : 'text-slate-500'}>
                  {item.icon}
                </span>
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Sidebar Footer */}
        <div className="p-3 border-t border-slate-800 bg-slate-950/40 text-[11px] space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full ${systemStatus?.database === 'OPERATIONAL' ? 'bg-emerald-500' : 'bg-amber-500'}`} />
              Telemetry
            </span>
            <span className="font-mono text-[10px] text-emerald-400 font-medium">
              {systemStatus?.database === 'OPERATIONAL' ? 'OPERATIONAL' : 'ONLINE'}
            </span>
          </div>
          <div className="flex items-center justify-center gap-2 text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">
            <Link to="/terms" className="hover:text-slate-400 transition-colors">Terms (Draft)</Link>
            <span>•</span>
            <Link to="/privacy" className="hover:text-slate-400 transition-colors">Privacy (Draft)</Link>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Top Header */}
        <header className="h-14 bg-slate-900 border-b border-slate-800 flex items-center justify-between px-4 sm:px-6 shrink-0 z-20">
          <div className="flex items-center gap-3 w-full max-w-lg">
            {/* Mobile Menu Toggle */}
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="lg:hidden p-1.5 text-slate-400 hover:text-slate-200 rounded border border-slate-800"
              aria-label="Open navigation menu"
            >
              <Menu size={18} />
            </button>

            {/* Global Search Input */}
            <div className="relative w-full" ref={searchRef}>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={15} />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    setIsSearchOpen(true);
                  }}
                  onFocus={() => setIsSearchOpen(true)}
                  placeholder="Search wallet address, TXID, IP, ASN, alert..."
                  className="w-full pl-9 pr-8 py-1.5 bg-slate-950 border border-slate-800 rounded text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery('')}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                    aria-label="Clear search"
                  >
                    <X size={13} />
                  </button>
                )}
              </div>

              {/* Search Dropdown Results */}
              {isSearchOpen && searchQuery.length >= 2 && (
                <div className="absolute top-full left-0 right-0 mt-1.5 bg-slate-900 border border-slate-800 rounded shadow-xl overflow-hidden max-h-96 z-50">
                  {isSearching ? (
                    <div className="p-4 text-xs text-slate-400 text-center font-mono">Searching entity index...</div>
                  ) : searchData?.results && searchData.results.length > 0 ? (
                    <div className="divide-y divide-slate-800 overflow-y-auto max-h-80">
                      {searchData.results.map((r: any, idx: number) => (
                        <button
                          key={idx}
                          onClick={() => handleSearchResultClick(r.url)}
                          className="w-full px-3.5 py-2 text-left flex items-center justify-between hover:bg-slate-850 transition-colors cursor-pointer"
                        >
                          <div className="truncate pr-3">
                            <div className="flex items-center gap-2">
                              <span className="text-[9px] font-mono px-1 py-0.2 rounded bg-slate-800 text-slate-300 border border-slate-700">
                                {r.type}
                              </span>
                              <span className="text-xs font-mono font-medium text-white truncate">
                                {r.type === 'WALLET' ? truncateAddress(r.label) : r.label}
                              </span>
                            </div>
                            <div className="text-[11px] text-slate-400 truncate mt-0.5">{r.subtitle}</div>
                          </div>
                          <ChevronRight size={13} className="text-slate-500 shrink-0" />
                        </button>
                      ))}
                    </div>
                  ) : (
                    <div className="p-4 text-xs text-slate-400 text-center font-mono">
                      No entities matching "{searchQuery}"
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Right Session & Controls */}
          <div className="flex items-center gap-2.5 sm:gap-3 shrink-0">
            <ThemeToggle />
            
            <div className="hidden sm:flex items-center gap-1.5 text-xs font-mono px-2.5 py-1 rounded bg-slate-850 border border-slate-800 text-slate-300">
              <UserIcon size={12} className="text-slate-400" />
              <span>INVESTIGATOR</span>
            </div>

            <button
              onClick={handleLogout}
              title="Logout from platform session"
              aria-label="Logout"
              className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-850 rounded border border-transparent hover:border-slate-800 transition-colors cursor-pointer"
            >
              <LogOut size={15} />
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 relative">
          <Suspense
            fallback={
              <div className="space-y-4 p-2 animate-pulse">
                <div className="h-8 bg-slate-800/60 rounded w-1/3"></div>
                <div className="h-4 bg-slate-800/40 rounded w-1/2"></div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
                  <div className="h-24 bg-slate-800/40 rounded-xl"></div>
                  <div className="h-24 bg-slate-800/40 rounded-xl"></div>
                  <div className="h-24 bg-slate-800/40 rounded-xl"></div>
                  <div className="h-24 bg-slate-800/40 rounded-xl"></div>
                </div>
                <div className="h-72 bg-slate-800/30 rounded-xl mt-6"></div>
              </div>
            }
          >
            <Outlet />
          </Suspense>
        </main>
      </div>
    </div>
  );
}
