import React, { useState } from 'react';
import { useAuditLogs } from '../api/hooks';
import { PageHeader } from '../components/ui/PageHeader';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { Shield, User, Clock, Terminal, ChevronRight, Filter, Laptop } from 'lucide-react';
import { formatDate } from '../utils/format';

export default function AuditLogsPage() {
  const [selectedAction, setSelectedAction] = useState<string>('');
  const [expandedLog, setExpandedLog] = useState<number | null>(null);

  const { data, isLoading, error } = useAuditLogs({
    action: selectedAction || undefined,
    limit: 100,
    offset: 0
  });

  const logs = data?.audit_logs || [];

  const actionTypes = [
    { label: 'All Actions', value: '' },
    { label: 'User Logins', value: 'USER_LOGIN' },
    { label: 'Dataset Uploads', value: 'DATASET_UPLOAD' },
    { label: 'Case Creation', value: 'CASE_CREATED' },
    { label: 'Report Exports', value: 'REPORT_EXPORTED' },
  ];

  const getActionBadgeClass = (action: string) => {
    switch (action) {
      case 'USER_LOGIN':
        return 'bg-emerald-500/20 text-emerald-400';
      case 'DATASET_UPLOAD':
        return 'bg-blue-500/20 text-blue-400';
      case 'CASE_CREATED':
        return 'bg-purple-500/20 text-purple-400';
      case 'REPORT_EXPORTED':
        return 'bg-amber-500/20 text-amber-400';
      default:
        return 'bg-slate-800 text-slate-300';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <PageHeader
          title="Forensic Audit Trail & Chain of Custody"
          description="Immutable chronological record of investigator interactions, data modifications, and report generations"
        />

        {/* Action Filter Pills */}
        <div className="flex flex-wrap gap-2">
          {actionTypes.map((t) => (
            <button
              key={t.value}
              onClick={() => setSelectedAction(t.value)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                selectedAction === t.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
        </div>
      ) : error ? (
        <ErrorState message="Failed to load audit logs" />
      ) : logs.length === 0 ? (
        <EmptyState
          icon={<Terminal className="text-slate-600" size={40} />}
          title="No Audit Logs Recorded"
          description="Investigative events and user interactions will be logged immutably in this audit repository."
        />
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <span className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Shield size={14} className="text-blue-400" />
              Audit Repository ({data?.total || logs.length} Records)
            </span>
            <span className="text-xs text-slate-500">
              Preserved with IP & User Attribution
            </span>
          </div>

          <div className="divide-y divide-slate-800">
            {logs.map((log: any) => {
              const isExpanded = expandedLog === log.id;
              return (
                <div key={log.id} className="transition-colors hover:bg-slate-800/30">
                  <div
                    onClick={() => setExpandedLog(isExpanded ? null : log.id)}
                    className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-3 cursor-pointer select-none"
                  >
                    <div className="flex items-start md:items-center gap-3">
                      <div className="p-2 rounded-lg bg-slate-800 text-slate-400 mt-0.5 md:mt-0">
                        <Terminal size={16} />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${getActionBadgeClass(log.action)}`}>
                            {log.action}
                          </span>
                          <span className="text-xs font-semibold text-white">
                            {log.username}
                          </span>
                          {log.entity_type && (
                            <span className="text-[10px] font-mono text-slate-500">
                              [{log.entity_type} {log.entity_id ? `:${log.entity_id}` : ''}]
                            </span>
                          )}
                        </div>
                        <div className="text-[11px] text-slate-400 mt-0.5 flex items-center gap-2">
                          <Clock size={12} />
                          <span>{formatDate(log.timestamp)}</span>
                          <span>•</span>
                          <Laptop size={12} />
                          <span className="font-mono">{log.ip_address}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-4 justify-between md:justify-end">
                      <ChevronRight
                        size={18}
                        className={`text-slate-500 transition-transform ${isExpanded ? 'rotate-90 text-blue-400' : ''}`}
                      />
                    </div>
                  </div>

                  {isExpanded && (
                    <div className="border-t border-slate-800 p-4 bg-slate-950/80">
                      <div className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">
                        Metadata & Operation Payload:
                      </div>
                      <pre className="text-[11px] font-mono text-slate-300 bg-slate-900 p-3 rounded-lg overflow-x-auto border border-slate-800">
                        {JSON.stringify(log.details, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
