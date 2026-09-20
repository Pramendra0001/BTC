import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { apiClient } from '../api/client';
import { ShieldAlert, Lock, User, Mail, ArrowRight, CheckCircle2, AlertCircle, UserPlus, LogIn } from 'lucide-react';

export default function LoginPage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<'login' | 'register'>('login');

  // Login form state - strictly no hardcoded credentials
  const [loginUsername, setLoginUsername] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

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
        setErrorMsg('Authentication server did not return a valid session token.');
      }
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Invalid username or password credentials');
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
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center items-center p-4 text-slate-100 font-sans">
      <div className="w-full max-w-md space-y-5">
        {/* Brand Header */}
        <div className="text-center space-y-1.5">
          <div className="w-10 h-10 rounded bg-slate-900 border border-slate-800 flex items-center justify-center text-blue-400 mx-auto">
            <ShieldAlert size={22} />
          </div>
          <h1 className="text-xl font-bold font-mono tracking-tight text-white">
            BTC-SHIELD
          </h1>
          <p className="text-xs text-slate-400">
            Bitcoin Transaction & Network Intelligence Platform
          </p>
          <div className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">
            Autonomous Transaction & Network Intelligence
          </div>
        </div>

        {/* Authentication Box */}
        <div className="bg-slate-900 border border-slate-800 rounded p-6 space-y-4 shadow-xl">
          {/* Mode Switch Tabs */}
          <div className="flex bg-slate-850 border border-slate-800 rounded p-0.5 gap-1">
            <button
              type="button"
              onClick={() => handleModeSwitch('login')}
              className={`flex-1 py-1.5 px-3 rounded text-xs font-mono font-medium transition flex items-center justify-center gap-1.5 cursor-pointer ${
                mode === 'login'
                  ? 'bg-slate-800 text-white border border-slate-700 shadow-xs'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <LogIn size={13} />
              Sign In
            </button>
            <button
              type="button"
              onClick={() => handleModeSwitch('register')}
              className={`flex-1 py-1.5 px-3 rounded text-xs font-mono font-medium transition flex items-center justify-center gap-1.5 cursor-pointer ${
                mode === 'register'
                  ? 'bg-slate-800 text-white border border-slate-700 shadow-xs'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <UserPlus size={13} />
              Register Account
            </button>
          </div>

          <div className="border-b border-slate-800 pb-2.5">
            <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-white">
              {mode === 'login' ? 'Investigator Authentication' : 'Create New Investigator Account'}
            </h2>
            <p className="text-[11px] text-slate-400 mt-0.5">
              {mode === 'login'
                ? 'Enter authorized credentials to access intelligence feeds'
                : 'Self-registered accounts are granted secure VIEWER inspection privileges'}
            </p>
          </div>

          {successMsg && (
            <div className="p-2.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-400 flex items-center gap-2 font-mono">
              <CheckCircle2 size={14} className="shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          {errorMsg && (
            <div className="p-2.5 rounded bg-rose-500/10 border border-rose-500/30 text-xs text-rose-400 flex items-center gap-2 font-mono">
              <AlertCircle size={14} className="shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {mode === 'login' ? (
            <form onSubmit={handleLogin} className="space-y-3.5">
              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">INVESTIGATOR ID / USERNAME</label>
                <div className="relative">
                  <User className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" size={14} />
                  <input
                    type="text"
                    required
                    autoComplete="username"
                    value={loginUsername}
                    onChange={(e) => setLoginUsername(e.target.value)}
                    className="w-full pl-8 pr-3 py-1.5 bg-slate-950 border border-slate-800 rounded text-xs font-mono text-white focus:outline-none focus:border-blue-500"
                    placeholder="Enter investigator ID or username"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">SECURITY ACCESS KEY / PASSWORD</label>
                <div className="relative">
                  <Lock className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" size={14} />
                  <input
                    type="password"
                    required
                    autoComplete="current-password"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    className="w-full pl-8 pr-3 py-1.5 bg-slate-950 border border-slate-800 rounded text-xs font-mono text-white focus:outline-none focus:border-blue-500"
                    placeholder="Enter security access key"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded transition flex items-center justify-center gap-2 shadow-xs cursor-pointer"
              >
                {isLoading ? 'Authenticating...' : (
                  <>
                    Authenticate Session <ArrowRight size={13} />
                  </>
                )}
              </button>
            </form>
          ) : (
            <form onSubmit={handleRegister} className="space-y-3">
              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">DESIRED USERNAME</label>
                <div className="relative">
                  <User className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" size={14} />
                  <input
                    type="text"
                    required
                    autoComplete="username"
                    value={regUsername}
                    onChange={(e) => setRegUsername(e.target.value)}
                    className="w-full pl-8 pr-3 py-1.5 bg-slate-950 border border-slate-800 rounded text-xs font-mono text-white focus:outline-none focus:border-blue-500"
                    placeholder="Min. 3 characters (e.g. investigator)"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">EMAIL ADDRESS</label>
                <div className="relative">
                  <Mail className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" size={14} />
                  <input
                    type="email"
                    required
                    autoComplete="email"
                    value={regEmail}
                    onChange={(e) => setRegEmail(e.target.value)}
                    className="w-full pl-8 pr-3 py-1.5 bg-slate-950 border border-slate-800 rounded text-xs font-mono text-white focus:outline-none focus:border-blue-500"
                    placeholder="e.g. investigator@example.com"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">PASSWORD</label>
                <div className="relative">
                  <Lock className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" size={14} />
                  <input
                    type="password"
                    required
                    autoComplete="new-password"
                    value={regPassword}
                    onChange={(e) => setRegPassword(e.target.value)}
                    className="w-full pl-8 pr-3 py-1.5 bg-slate-950 border border-slate-800 rounded text-xs font-mono text-white focus:outline-none focus:border-blue-500"
                    placeholder="Min. 8 characters"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">CONFIRM PASSWORD</label>
                <div className="relative">
                  <Lock className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" size={14} />
                  <input
                    type="password"
                    required
                    autoComplete="new-password"
                    value={regConfirmPassword}
                    onChange={(e) => setRegConfirmPassword(e.target.value)}
                    className="w-full pl-8 pr-3 py-1.5 bg-slate-950 border border-slate-800 rounded text-xs font-mono text-white focus:outline-none focus:border-blue-500"
                    placeholder="Re-enter your password"
                  />
                </div>
              </div>

              <div className="p-2 rounded bg-slate-850 border border-slate-800 text-[10px] text-slate-400 font-mono leading-relaxed">
                Role: <span className="font-bold text-slate-200">VIEWER</span>. Read-only inspection privileges for all intelligence feeds and graphs.
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded transition flex items-center justify-center gap-2 shadow-xs cursor-pointer"
              >
                {isLoading ? 'Creating Account...' : (
                  <>
                    Create Account <UserPlus size={13} />
                  </>
                )}
              </button>
            </form>
          )}
        </div>

        {/* Legal & Terms Footer */}
        <div className="flex items-center justify-center gap-3 text-[11px] font-mono text-slate-500">
          <Link to="/terms" className="hover:text-slate-400 transition-colors">Terms of Service (Draft)</Link>
          <span>•</span>
          <Link to="/privacy" className="hover:text-slate-400 transition-colors">Privacy Policy (Draft)</Link>
        </div>
      </div>
    </div>
  );
}
