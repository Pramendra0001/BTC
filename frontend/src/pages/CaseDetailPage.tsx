import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useCase, useUpdateCase, useAddNote, useCaseReport } from '../api/hooks';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { 
  Briefcase, ShieldCheck, User, Clock, FileText, Send, 
  ExternalLink, Network, CheckCircle2, Download, Printer, AlertTriangle
} from 'lucide-react';
import { getPriorityColor, getStatusColor, formatDate, truncateAddress } from '../utils/format';

export default function CaseDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [activeTab, setActiveTab] = useState<'entities' | 'evidence' | 'notes' | 'report'>('entities');
  const [newNote, setNewNote] = useState('');

  const { data: caseItem, isLoading, error, refetch } = useCase(id || '');
  const { data: reportData } = useCaseReport(id || '');

  const updateCaseMutation = useUpdateCase();
  const addNoteMutation = useAddNote();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>
        <Skeleton className="h-80 w-full" />
      </div>
    );
  }

  if (error || !caseItem) {
    return <ErrorState message="Failed to load investigation case." onRetry={() => refetch()} />;
  }

  const pColor = getPriorityColor(caseItem.priority);
  const sColor = getStatusColor(caseItem.status);

  const handleStatusChange = async (newStatus: string) => {
    try {
      await updateCaseMutation.mutateAsync({
        id: caseItem.id,
        data: { status: newStatus },
      });
    } catch (err) {
      console.error('Failed to update status:', err);
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNote.trim()) return;
    try {
      await addNoteMutation.mutateAsync({
        id: caseItem.id,
        content: newNote.trim(),
      });
      setNewNote('');
    } catch (err) {
      console.error('Failed to add note:', err);
    }
  };

  const handleDownloadReport = () => {
    if (!reportData) return;
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `BTC-SHIELD-Case-${caseItem.id}-Report.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
        <Link to="/cases" className="hover:text-slate-300">CASES</Link>
        <span>/</span>
        <span className="text-slate-200">CASE #{caseItem.id}</span>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 border border-slate-800 rounded-xl p-5">
        <div className="space-y-1.5">
          <div className="flex items-center gap-3">
            <h1 className="text-lg font-bold text-white font-mono flex items-center gap-2">
              <Briefcase className="text-blue-400" size={20} />
              {caseItem.title}
            </h1>
            <span className={`px-2.5 py-0.5 rounded text-xs font-bold font-mono ${pColor.bg} ${pColor.text} border ${pColor.border}`}>
              {caseItem.priority}
            </span>
          </div>
          <p className="text-xs text-slate-300 max-w-2xl">
            {caseItem.description || "No description provided."}
          </p>
          <div className="text-xs text-slate-400 font-mono flex items-center gap-4 pt-1 text-[11px]">
            <span>Opened: <strong className="text-slate-200">{formatDate(caseItem.created_at)}</strong></span>
            <span>Investigator: <strong className="text-slate-200">{caseItem.investigator || 'Admin'}</strong></span>
          </div>
        </div>

        {/* Status Dropdown */}
        <div className="flex items-center gap-3">
          <div className="text-xs text-slate-400">Status:</div>
          <select
            value={caseItem.status}
            onChange={(e) => handleStatusChange(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-xs font-mono text-white rounded-lg px-3 py-1.5 focus:outline-none focus:border-blue-500"
          >
            <option value="OPEN">OPEN</option>
            <option value="ACTIVE">ACTIVE</option>
            <option value="CLOSED">CLOSED</option>
          </select>
        </div>
      </div>

      {/* Case Overview KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400">Pinned Target Entities</div>
          <div className="text-xl font-bold font-mono text-blue-400 mt-1">
            {caseItem.entities?.length || 0} entities
          </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400">Attached Evidence Items</div>
          <div className="text-xl font-bold font-mono text-amber-400 mt-1">
            {caseItem.evidence?.length || 0} signals
          </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400">Investigator Logged Notes</div>
          <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
            {caseItem.notes?.length || 0} entries
          </div>
        </div>
      </div>

      {/* Workspace Tabs */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        <div className="flex border-b border-slate-800 px-4 bg-slate-950/40">
          {[
            { id: 'entities', label: `Pinned Entities (${caseItem.entities?.length || 0})` },
            { id: 'evidence', label: `Attached Evidence (${caseItem.evidence?.length || 0})` },
            { id: 'notes', label: `Investigator Notes (${caseItem.notes?.length || 0})` },
            { id: 'report', label: 'Forensic Report' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`py-3 px-4 text-xs font-medium border-b-2 transition ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="p-5">
          {/* Tab 1: Pinned Entities */}
          {activeTab === 'entities' && (
            <div className="space-y-3">
              {caseItem.entities && caseItem.entities.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {caseItem.entities.map((ent: any, idx: number) => {
                    const url = ent.type === 'WALLET' ? `/wallets/${ent.id}` : `/ips/${ent.id}`;
                    return (
                      <div key={idx} className="p-3.5 bg-slate-950 border border-slate-800 rounded-lg flex items-center justify-between">
                        <div className="truncate pr-3">
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-blue-400">
                              {ent.type}
                            </span>
                            <span className="font-mono text-xs text-white truncate">
                              {ent.type === 'WALLET' ? truncateAddress(ent.id, 12, 10) : ent.id}
                            </span>
                          </div>
                          <div className="text-[11px] text-slate-400 mt-1 font-mono">
                            Pinned: {formatDate(ent.added_at)}
                          </div>
                        </div>
                        <div className="flex items-center gap-2 shrink-0">
                          <Link
                            to={`/graph?entityType=${ent.type}&entityId=${encodeURIComponent(ent.id)}`}
                            title="View in Graph"
                            className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-blue-400"
                          >
                            <Network size={14} />
                          </Link>
                          <Link
                            to={url}
                            className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200"
                          >
                            <ExternalLink size={14} />
                          </Link>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-8 text-xs text-slate-400">
                  No entities pinned yet. Pin entities from Wallet, IP, or Alert details.
                </div>
              )}
            </div>
          )}

          {/* Tab 2: Attached Evidence */}
          {activeTab === 'evidence' && (
            <div className="space-y-3">
              {caseItem.evidence && caseItem.evidence.length > 0 ? (
                caseItem.evidence.map((ev: any) => (
                  <div key={ev.id} className="p-4 bg-slate-950 border border-slate-800 rounded-lg space-y-1.5">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-amber-400 border border-slate-700">
                          {ev.category} EVIDENCE
                        </span>
                        <span className="text-xs font-mono text-slate-400">
                          Target: <strong className="text-white">{truncateAddress(ev.entity_id, 10, 8)}</strong>
                        </span>
                      </div>
                      <span className="text-xs font-mono text-slate-400">
                        Strength: <strong className="text-white">{Math.round((ev.strength || 0) * 100)}%</strong>
                      </span>
                    </div>
                    <p className="text-xs text-slate-200 leading-relaxed">
                      {ev.observation}
                    </p>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-xs text-slate-400">
                  No evidence items attached yet.
                </div>
              )}
            </div>
          )}

          {/* Tab 3: Notes */}
          {activeTab === 'notes' && (
            <div className="space-y-4">
              {/* Note input */}
              <form onSubmit={handleAddNote} className="space-y-2">
                <textarea
                  rows={2}
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  placeholder="Record an investigative observation, rationale, or hypothesis..."
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-blue-500"
                />
                <div className="flex justify-end">
                  <button
                    type="submit"
                    disabled={addNoteMutation.isPending || !newNote.trim()}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition"
                  >
                    <Send size={12} /> {addNoteMutation.isPending ? 'Logging...' : 'Log Note'}
                  </button>
                </div>
              </form>

              {/* Notes list */}
              <div className="space-y-3 pt-2">
                {caseItem.notes && caseItem.notes.length > 0 ? (
                  caseItem.notes.map((n: any) => (
                    <div key={n.id} className="p-3.5 bg-slate-950 border border-slate-800 rounded-lg space-y-1">
                      <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
                        <span className="text-blue-400 font-bold">{n.author}</span>
                        <span>{formatDate(n.created_at)}</span>
                      </div>
                      <p className="text-xs text-slate-200 leading-relaxed whitespace-pre-wrap">
                        {n.content}
                      </p>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-6 text-xs text-slate-400">
                    No notes recorded for this case yet.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Tab 4: Forensic Report */}
          {activeTab === 'report' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-white">Automated Forensic Intelligence Report</h3>
                  <p className="text-xs text-slate-400">Exportable dossier containing case metadata, entities, and evidence audit trails</p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => window.print()}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs rounded-lg border border-slate-700 transition"
                  >
                    <Printer size={13} /> Print
                  </button>
                  <button
                    onClick={handleDownloadReport}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium rounded-lg transition shadow"
                  >
                    <Download size={13} /> Download JSON
                  </button>
                </div>
              </div>

              {/* Report Preview */}
              <div className="bg-slate-950 p-6 rounded-xl border border-slate-800 font-mono text-xs space-y-4">
                <div className="border-b border-slate-800 pb-3 flex items-center justify-between">
                  <div>
                    <div className="text-sm font-bold text-white">BTC-SHIELD FORENSIC CASE DOSSIER</div>
                    <div className="text-slate-400 text-[11px]">CASE ID: #{caseItem.id} • PRIORITY: {caseItem.priority}</div>
                  </div>
                  <div className="text-right text-slate-400 text-[11px]">
                    GENERATED: {new Date().toISOString()}
                  </div>
                </div>

                <div>
                  <span className="text-slate-400 uppercase">TITLE: </span>
                  <span className="text-white font-bold">{caseItem.title}</span>
                </div>

                <div>
                  <span className="text-slate-400 uppercase">STATUS: </span>
                  <span className="text-emerald-400 font-bold">{caseItem.status}</span>
                </div>

                <div>
                  <span className="text-slate-400 uppercase">SCOPE / SUMMARY: </span>
                  <p className="text-slate-300 font-sans mt-1 text-xs">{caseItem.description || "N/A"}</p>
                </div>

                <div className="pt-2 border-t border-slate-800">
                  <span className="text-slate-400 uppercase">IDENTIFIED TARGET ENTITIES ({caseItem.entities?.length || 0}):</span>
                  <ul className="list-disc list-inside mt-1 space-y-1 text-slate-300 text-[11px]">
                    {caseItem.entities?.map((e: any, i: number) => (
                      <li key={i}>{e.type}: {e.id} (Pinned: {e.added_at})</li>
                    ))}
                  </ul>
                </div>

                <div className="pt-2 border-t border-slate-800">
                  <span className="text-slate-400 uppercase">FORMAL EVIDENCE AUDIT ({caseItem.evidence?.length || 0}):</span>
                  <div className="mt-2 space-y-2">
                    {caseItem.evidence?.map((ev: any, i: number) => (
                      <div key={i} className="p-2.5 bg-slate-900 rounded border border-slate-800/80 text-[11px]">
                        <span className="text-amber-400">[{ev.category}]</span> Strength: {Math.round((ev.strength || 0) * 100)}% — {ev.observation}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="p-3 bg-slate-900/60 rounded border border-slate-800 text-[10px] text-slate-400">
                  <strong>LEGAL DISCLAIMER:</strong> This report is generated from algorithmic intelligence on synthetic Bitcoin and network telemetry data. Findings constitute investigative leads requiring human corroboration, not judicial determination.
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
