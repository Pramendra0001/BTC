import { useState } from 'react';
import { useCases, useCreateCase } from '../api/hooks';
import { PageHeader } from '../components/ui/PageHeader';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { Link, useNavigate } from 'react-router-dom';
import { Briefcase, Plus, Filter, ChevronRight, Clock, FileText, User } from 'lucide-react';
import { getPriorityColor, getStatusColor, formatDate } from '../utils/format';

export default function CasesPage() {
  const navigate = useNavigate();
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('MEDIUM');

  const { data, isLoading, error, refetch } = useCases({
    status: statusFilter === 'ALL' ? undefined : statusFilter,
  });

  const createCaseMutation = useCreateCase();

  const cases = data?.cases || [];
  const total = data?.total || 0;

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title) return;
    try {
      const res = await createCaseMutation.mutateAsync({
        title,
        description,
        priority,
      });
      setCreateModalOpen(false);
      setTitle('');
      setDescription('');
      navigate(`/cases/${res.id}`);
    } catch (err) {
      console.error('Failed to create case:', err);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Cases & Reports" 
        description="Formal investigative dossiers organizing entities, network evidence, notes, and forensic reports" 
        actions={
          <button
            onClick={() => setCreateModalOpen(true)}
            className="inline-flex items-center gap-2 px-3.5 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium rounded-lg transition shadow"
          >
            <Plus size={14} /> New Investigation Case
          </button>
        }
      />

      {/* Filter Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Filter size={14} className="text-slate-400" />
          <span className="text-xs text-slate-400 font-mono">STATUS:</span>
          {['ALL', 'OPEN', 'ACTIVE', 'CLOSED'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition ${
                statusFilter === st
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
        <div className="text-xs text-slate-400 font-mono">
          Total Cases: <strong className="text-white">{total}</strong>
        </div>
      </div>

      {/* Cases Table */}
      {isLoading ? (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
        </div>
      ) : error ? (
        <ErrorState message="Failed to load investigative cases." onRetry={() => refetch()} />
      ) : cases.length === 0 ? (
        <EmptyState
          icon={<Briefcase size={32} />}
          title="No Investigation Cases Found"
          description="Create your first investigative case to assemble forensic evidence and generate comprehensive intelligence reports."
          action={
            <button
              onClick={() => setCreateModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium rounded-lg transition"
            >
              <Plus size={14} /> Create Case
            </button>
          }
        />
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/70 text-slate-400 border-b border-slate-800 font-mono text-[11px] uppercase">
              <tr>
                <th className="py-3 px-4">Case ID</th>
                <th className="py-3 px-4">Priority</th>
                <th className="py-3 px-4">Title</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Investigator</th>
                <th className="py-3 px-4">Created</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {cases.map((c: any) => {
                const pColor = getPriorityColor(c.priority);
                const sColor = getStatusColor(c.status);
                return (
                  <tr key={c.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-4 font-mono font-bold text-slate-300">
                      #{c.id}
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${pColor.bg} ${pColor.text} border ${pColor.border}`}>
                        {c.priority}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <Link to={`/cases/${c.id}`} className="text-sm font-semibold text-white hover:text-blue-400">
                        {c.title}
                      </Link>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono ${sColor.bg} ${sColor.text} border ${sColor.border}`}>
                        {c.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-300 font-mono flex items-center gap-1.5 pt-4">
                      <User size={13} className="text-slate-400" />
                      Investigator #{c.investigator_id || 1}
                    </td>
                    <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">
                      {formatDate(c.created_at)}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Link
                        to={`/cases/${c.id}`}
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-blue-600/10 hover:bg-blue-600/20 text-blue-400 text-xs font-medium border border-blue-500/20 transition"
                      >
                        Workspace <ChevronRight size={12} />
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Create Case Modal */}
      {createModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <form onSubmit={handleCreate} className="bg-slate-900 border border-slate-800 rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Briefcase size={18} className="text-blue-400" />
              New Investigation Case
            </h3>
            <p className="text-xs text-slate-400">
              Establish a case dossier to track suspicious blockchain transactions and network telemetry.
            </p>

            <div className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Case Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Operation Tumbler-04"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Priority</label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="CRITICAL">CRITICAL</option>
                  <option value="HIGH">HIGH</option>
                  <option value="MEDIUM">MEDIUM</option>
                  <option value="LOW">LOW</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Description / Investigative Scope</label>
                <textarea
                  rows={3}
                  placeholder="Summary of targets, suspected behavioral anomalies, or intelligence objectives..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setCreateModalOpen(false)}
                className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs rounded-lg transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={createCaseMutation.isPending || !title}
                className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition"
              >
                {createCaseMutation.isPending ? 'Opening...' : 'Create Case'}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
