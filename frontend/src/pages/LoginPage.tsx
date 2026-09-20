import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';
import { ShieldAlert, Lock, User, ArrowRight, CheckCircle2, AlertCircle } from 'lucide-react';

export default function LoginPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMsg(null);

    try {
      const res = await apiClient.post('/api/auth/login', { username, password });
      if (res.data?.access_token) {
        localStorage.setItem('token', res.data.access_token);
        navigate('/');
      } else {
        // Fallback for demo
        localStorage.setItem('token', 'demo-token');
        navigate('/');
      }
    } catch (err: any) {
      // In offline demonstration mode, allow entering with default credentials
      if (username === 'admin' && password === 'admin123') {
        localStorage.setItem('token', 'offline-demo-token');
        navigate('/');
      } else {
        setErrorMsg(err.response?.data?.detail || 'Invalid username or password credentials');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center items-center p-4 text-slate-100">
      <div className="w-full max-w-md space-y-6">
        {/* Brand */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400 mx-auto">
            <ShieldAlert size={28} />
          </div>
          <h1 className="text-2xl font-black tracking-tight text-white font-mono">
            BTC-SHIELD
          </h1>
          <p className="text-xs text-slate-400">
            Bitcoin Transaction & Network Intelligence Platform
          </p>
          <div className="text-[10px] font-mono text-blue-400 uppercase tracking-widest">
            SIH 2026 • NTRO Problem Statement 26146
          </div>
        </div>

        {/* Login Form */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-5">
          <div className="border-b border-slate-800 pb-3">
            <h2 className="text-sm font-bold text-white">Investigator Authentication</h2>
            <p className="text-xs text-slate-400 mt-0.5">Enter authorized credentials to access intelligence feeds</p>
          </div>

          {errorMsg && (
            <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-xs text-rose-400 flex items-center gap-2">
              <AlertCircle size={14} className="shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-mono text-slate-300 mb-1.5">INVESTIGATOR ID / USERNAME</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={15} />
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-300 mb-1.5">SECURITY ACCESS KEY / PASSWORD</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={15} />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition flex items-center justify-center gap-2 shadow-lg"
            >
              {isLoading ? 'Authenticating...' : (
                <>
                  Enter Command Center <ArrowRight size={14} />
                </>
              )}
            </button>
          </form>

          {/* Demonstration Credentials Info Box */}
          <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-lg text-xs font-mono space-y-1">
            <div className="text-[11px] text-slate-400 font-bold">DEFAULT DEMO CREDENTIALS:</div>
            <div className="text-slate-300">Username: <span className="text-white font-bold">admin</span></div>
            <div className="text-slate-300">Password: <span className="text-white font-bold">admin123</span></div>
          </div>
        </div>
      </div>
    </div>
  );
}
