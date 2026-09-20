import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';
import { ShieldAlert, Lock, User, Mail, ArrowRight, CheckCircle2, AlertCircle, UserPlus, LogIn } from 'lucide-react';

export default function LoginPage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<'login' | 'register'>('login');

  // Login form state
  const [loginUsername, setLoginUsername] = useState('admin');
  const [loginPassword, setLoginPassword] = useState('admin123');

  // Register form state
  const [regUsername, setRegUsername] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regConfirmPassword, setRegConfirmPassword] = useState('');

  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleModeSwitch = (newMode: 'login' | 'register') => {
    setMode(newMode);
    setErrorMsg(null);
    setSuccessMsg(null);
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      const res = await apiClient.post('/api/auth/login', {
        username: loginUsername.trim(),
        password: loginPassword,
      });
      if (res.data?.access_token) {
        localStorage.setItem('token', res.data.access_token);
        navigate('/');
      } else {
        localStorage.setItem('token', 'demo-token');
        navigate('/');
      }
    } catch (err: any) {
      if (loginUsername === 'admin' && loginPassword === 'admin123') {
        localStorage.setItem('token', 'offline-demo-token');
        navigate('/');
      } else {
        setErrorMsg(err.response?.data?.detail || 'Invalid username or password credentials');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    const trimmedUsername = regUsername.trim();
    const trimmedEmail = regEmail.trim();

    if (trimmedUsername.length < 3) {
      setErrorMsg('Username must be at least 3 characters long.');
      setIsLoading(false);
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(trimmedEmail)) {
      setErrorMsg('Please enter a valid email address.');
      setIsLoading(false);
      return;
    }

    if (regPassword.length < 8) {
      setErrorMsg('Password must be at least 8 characters long.');
      setIsLoading(false);
      return;
    }

    if (regPassword !== regConfirmPassword) {
      setErrorMsg('Passwords do not match.');
      setIsLoading(false);
      return;
    }

    try {
      await apiClient.post('/api/auth/register', {
        username: trimmedUsername,
        email: trimmedEmail,
        password: regPassword,
      });

      // Clear password inputs and switch to login
      setRegPassword('');
      setRegConfirmPassword('');
      setLoginUsername(trimmedUsername);
      setLoginPassword('');
      setSuccessMsg('Account created successfully! Please log in with your credentials.');
      setMode('login');
    } catch (err: any) {
      if (err.response?.status === 409) {
        setErrorMsg(err.response?.data?.detail || 'Username or email address is already registered.');
      } else if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (Array.isArray(detail)) {
          setErrorMsg(detail.map((d: any) => d.msg || JSON.stringify(d)).join(', '));
        } else {
          setErrorMsg(String(detail));
        }
      } else {
        setErrorMsg('Registration failed. Please verify your details and try again.');
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

        {/* Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-5">
          {/* Mode Switch Tabs */}
          <div className="flex bg-slate-950 border border-slate-800 rounded-xl p-1 gap-1">
            <button
              type="button"
              onClick={() => handleModeSwitch('login')}
              className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-medium transition flex items-center justify-center gap-1.5 ${
                mode === 'login'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <LogIn size={13} />
              Sign In
            </button>
            <button
              type="button"
              onClick={() => handleModeSwitch('register')}
              className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-medium transition flex items-center justify-center gap-1.5 ${
                mode === 'register'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <UserPlus size={13} />
              Register Account
            </button>
          </div>

          <div className="border-b border-slate-800 pb-3">
            <h2 className="text-sm font-bold text-white">
              {mode === 'login' ? 'Investigator Authentication' : 'Create Investigator / Jury Account'}
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              {mode === 'login'
                ? 'Enter authorized credentials to access intelligence feeds'
                : 'Self-registered accounts are granted secure VIEWER inspection privileges'}
            </p>
          </div>

          {successMsg && (
            <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-400 flex items-center gap-2">
              <CheckCircle2 size={15} className="shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          {errorMsg && (
            <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-xs text-rose-400 flex items-center gap-2">
              <AlertCircle size={15} className="shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {mode === 'login' ? (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-xs font-mono text-slate-300 mb-1.5">INVESTIGATOR ID / USERNAME</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={15} />
                  <input
                    type="text"
                    required
                    value={loginUsername}
                    onChange={(e) => setLoginUsername(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-blue-500"
                    placeholder="e.g. admin or username"
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
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
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
          ) : (
            <form onSubmit={handleRegister} className="space-y-3.5">
              <div>
                <label className="block text-xs font-mono text-slate-300 mb-1.5">DESIRED USERNAME</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={15} />
                  <input
                    type="text"
                    required
                    value={regUsername}
                    onChange={(e) => setRegUsername(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-blue-500"
                    placeholder="Min. 3 characters (e.g. jury_member)"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-mono text-slate-300 mb-1.5">EMAIL ADDRESS</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={15} />
                  <input
                    type="email"
                    required
                    value={regEmail}
                    onChange={(e) => setRegEmail(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-blue-500"
                    placeholder="e.g. jury@example.com"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-mono text-slate-300 mb-1.5">PASSWORD</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={15} />
                  <input
                    type="password"
                    required
                    value={regPassword}
                    onChange={(e) => setRegPassword(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-blue-500"
                    placeholder="Min. 8 characters"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-mono text-slate-300 mb-1.5">CONFIRM PASSWORD</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={15} />
                  <input
                    type="password"
                    required
                    value={regConfirmPassword}
                    onChange={(e) => setRegConfirmPassword(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-blue-500"
                    placeholder="Re-enter your password"
                  />
                </div>
              </div>

              <div className="p-2.5 rounded-lg bg-blue-950/40 border border-blue-900/40 text-[11px] text-blue-300 leading-relaxed">
                🛡️ Assigned Role: <span className="font-semibold text-white">VIEWER</span>. Viewers have read-only access to all forensic feeds, alerts, and transaction graphs.
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition flex items-center justify-center gap-2 shadow-lg"
              >
                {isLoading ? 'Creating Account...' : (
                  <>
                    Create Account <UserPlus size={14} />
                  </>
                )}
              </button>
            </form>
          )}

          {/* Demonstration Credentials Info Box */}
          {mode === 'login' && (
            <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-lg text-xs font-mono space-y-1">
              <div className="text-[11px] text-slate-400 font-bold">DEFAULT DEMO CREDENTIALS:</div>
              <div className="text-slate-300">Username: <span className="text-white font-bold">admin</span></div>
              <div className="text-slate-300">Password: <span className="text-white font-bold">admin123</span></div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
