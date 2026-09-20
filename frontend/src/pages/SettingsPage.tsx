import React, { useState } from 'react';
import { useUsers, useUpdateUser, useJobs } from '../api/hooks';
import { PageHeader } from '../components/ui/PageHeader';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { Users, Shield, Cpu, Activity, CheckCircle2, AlertCircle, Clock, Check, Lock, Database, WifiOff } from 'lucide-react';
import { formatDate } from '../utils/format';

export default function SettingsPage() {
  const { data: users, isLoading: usersLoading, error: usersError } = useUsers();
  const updateUserMutation = useUpdateUser();
  const { data: jobs, isLoading: jobsLoading } = useJobs();

  const [notification, setNotification] = useState<string | null>(null);

  const handleRoleChange = (userId: number, newRole: string) => {
    updateUserMutation.mutate(
      { userId, data: { role: newRole } },
      {
        onSuccess: () => {
          setNotification(`User #${userId} role updated to ${newRole}`);
          setTimeout(() => setNotification(null), 3000);
        }
      }
    );
  };

  const handleStatusToggle = (userId: number, currentStatus: boolean) => {
    updateUserMutation.mutate(
      { userId, data: { is_active: !currentStatus } },
      {
        onSuccess: () => {
          setNotification(`User #${userId} active status changed.`);
          setTimeout(() => setNotification(null), 3000);
        }
      }
    );
  };

  const roles = ['ADMINISTRATOR', 'INVESTIGATOR', 'ANALYST', 'VIEWER'];

  return (
    <div className="space-y-6">
      <PageHeader
        title="System Settings & RBAC Management"
        description="User permissions, role-based access control, background job task monitors, and air-gapped environment telemetry"
      />

      {notification && (
        <div className="p-3 bg-emerald-500/20 border border-emerald-500/40 rounded-lg text-xs text-emerald-300 flex items-center gap-2">
          <CheckCircle2 size={16} />
          {notification}
        </div>
      )}

      {/* Deployment & Environment Banner */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-400">
            <WifiOff size={20} />
          </div>
          <div>
            <div className="text-xs font-bold text-white">SIH Air-Gapped Mode</div>
            <div className="text-[11px] text-slate-400">100% Offline execution • Zero external egress</div>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-blue-500/10 text-blue-400">
            <Database size={20} />
          </div>
          <div>
            <div className="text-xs font-bold text-white">Database Engine</div>
            <div className="text-[11px] text-slate-400">SQLite Dev / PostgreSQL Dual-Supported</div>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-purple-500/10 text-purple-400">
            <Lock size={20} />
          </div>
          <div>
            <div className="text-xs font-bold text-white">Security Hardening</div>
            <div className="text-[11px] text-slate-400">JWT (HS256) • Safe DefusedXML • Direct Bcrypt</div>
          </div>
        </div>
      </div>

      {/* User Management & RBAC Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
            <Users size={16} className="text-blue-400" />
            User Accounts & Role Assignments ({users?.length || 0})
          </h3>
          <span className="text-[11px] text-slate-400">
            Changes take effect immediately
          </span>
        </div>

        {usersLoading ? (
          <div className="p-6 space-y-3">
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
        ) : usersError ? (
          <div className="p-6">
            <ErrorState message="Failed to load user accounts" />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider bg-slate-950/40">
                  <th className="p-3">User</th>
                  <th className="p-3">Email</th>
                  <th className="p-3">Assigned Role</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Created</th>
                  <th className="p-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-slate-300">
                {users?.map((u: any) => (
                  <tr key={u.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="p-3 font-semibold text-white flex items-center gap-2">
                      <div className="w-7 h-7 rounded-full bg-slate-800 flex items-center justify-center text-slate-300 font-bold uppercase text-xs">
                        {u.username.slice(0, 2)}
                      </div>
                      {u.username}
                    </td>
                    <td className="p-3 font-mono text-slate-400">{u.email}</td>
                    <td className="p-3">
                      <select
                        value={u.role}
                        onChange={(e) => handleRoleChange(u.id, e.target.value)}
                        className="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200 focus:outline-none focus:border-blue-500 font-mono"
                      >
                        {roles.map((r) => (
                          <option key={r} value={r}>
                            {r}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td className="p-3">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                          u.is_active ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-800 text-slate-500'
                        }`}
                      >
                        {u.is_active ? 'ACTIVE' : 'INACTIVE'}
                      </span>
                    </td>
                    <td className="p-3 text-slate-500 text-[11px]">{formatDate(u.created_at)}</td>
                    <td className="p-3 text-right">
                      <button
                        onClick={() => handleStatusToggle(u.id, u.is_active)}
                        className={`px-2.5 py-1 rounded text-[11px] font-semibold transition-colors ${
                          u.is_active
                            ? 'bg-rose-500/20 text-rose-300 hover:bg-rose-500/30'
                            : 'bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30'
                        }`}
                      >
                        {u.is_active ? 'Deactivate' : 'Activate'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Background Pipeline Jobs */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
            <Activity size={16} className="text-emerald-400" />
            Asynchronous Pipeline Task Engine
          </h3>
          <span className="text-[11px] font-mono text-slate-500">
            Auto-refreshing (5s interval)
          </span>
        </div>

        {jobsLoading ? (
          <div className="p-6 space-y-3">
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-10 w-full" />
          </div>
        ) : (
          <div className="divide-y divide-slate-800">
            {jobs?.map((job: any) => (
              <div key={job.job_id} className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        job.status === 'COMPLETED'
                          ? 'bg-emerald-500/20 text-emerald-400'
                          : job.status === 'RUNNING'
                          ? 'bg-blue-500/20 text-blue-400 animate-pulse'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {job.status}
                    </span>
                    <span className="font-mono text-xs font-bold text-white">{job.description}</span>
                  </div>
                  <div className="text-[11px] text-slate-400 font-mono">
                    {job.message}
                  </div>
                  <div className="text-[10px] text-slate-500 flex items-center gap-3">
                    <span>ID: {job.job_id}</span>
                    <span>•</span>
                    <span>Started: {formatDate(job.started_at)}</span>
                    {job.duration_seconds && (
                      <>
                        <span>•</span>
                        <span>Duration: {job.duration_seconds}s</span>
                      </>
                    )}
                  </div>
                </div>

                <div className="w-full md:w-48 space-y-1">
                  <div className="flex justify-between text-[11px] text-slate-400">
                    <span>Progress</span>
                    <span className="font-mono font-bold text-white">{job.progress_pct}%</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-2 rounded-full ${
                        job.status === 'COMPLETED'
                          ? 'bg-emerald-500'
                          : job.status === 'RUNNING'
                          ? 'bg-blue-500'
                          : 'bg-slate-600'
                      }`}
                      style={{ width: `${job.progress_pct}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* RBAC Permission Matrix Reference */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
        <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
          <Shield size={16} className="text-purple-400" />
          Role-Based Access Control (RBAC) Authority Matrix
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs">
          <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80 space-y-1">
            <div className="font-bold text-purple-400">ADMINISTRATOR</div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Full platform sovereignty: user registration, role reassignment, database reset, system config.
            </p>
          </div>
          <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80 space-y-1">
            <div className="font-bold text-blue-400">INVESTIGATOR</div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Case creation, note drafting, evidence linking, report export, alert triage & adjudication.
            </p>
          </div>
          <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80 space-y-1">
            <div className="font-bold text-emerald-400">ANALYST</div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Dataset upload, pipeline triggering, model training & parameter tuning, graph queries.
            </p>
          </div>
          <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80 space-y-1">
            <div className="font-bold text-slate-400">VIEWER</div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Read-only inspection of dashboards, alerts, transaction graphs, and historical timelines.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
