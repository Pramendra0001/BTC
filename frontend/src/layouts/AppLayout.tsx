import { Outlet, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, AlertCircle, Wallet, ArrowRightLeft, Network, Activity, Briefcase, Database, Cpu, Globe } from 'lucide-react';
import { cn } from '../components/ui/Badge';

const navItems = [
  { name: 'Dashboard', path: '/', icon: <LayoutDashboard size={18} /> },
  { name: 'Alerts', path: '/alerts', icon: <AlertCircle size={18} /> },
  { name: 'Wallets', path: '/wallets', icon: <Wallet size={18} /> },
  { name: 'Transactions', path: '/transactions', icon: <ArrowRightLeft size={18} /> },
  { name: 'Graph', path: '/graph', icon: <Network size={18} /> },
  { name: 'Cases', path: '/cases', icon: <Briefcase size={18} /> },
  { name: 'Datasets', path: '/datasets', icon: <Database size={18} /> },
  { name: 'Models', path: '/models', icon: <Cpu size={18} /> },
  { name: 'System', path: '/system', icon: <Activity size={18} /> },
];

export default function AppLayout() {
  const location = useLocation();
  return (
    <div className="flex h-screen overflow-hidden bg-slate-950">
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col hidden md:flex">
        <div className="p-4 border-b border-slate-800">
          <div className="text-xl font-bold text-white flex items-center gap-2">
            <Globe className="text-blue-500" /> BTC-SHIELD
          </div>
        </div>
        <nav className="flex-1 overflow-y-auto p-4 space-y-1">
          {navItems.map((item) => (
            <Link key={item.path} to={item.path} className={cn("flex items-center gap-3 px-3 py-2 rounded-md transition", location.pathname === item.path ? "bg-slate-800 text-white" : "text-slate-400 hover:text-white hover:bg-slate-800/50")}>
              {item.icon}
              {item.name}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="flex-1 flex flex-col h-full overflow-hidden">
        <header className="h-16 bg-slate-900 border-b border-slate-800 flex items-center justify-between px-6">
          <div className="text-slate-400">Global Search...</div>
          <div className="flex items-center gap-4">
            <div className="w-8 h-8 bg-slate-700 rounded-full"></div>
          </div>
        </header>
        <div className="flex-1 overflow-y-auto p-6 relative">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
