import { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAlert, useAlertExplain, useCreateCase, useEvidenceList } from '../api/hooks';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { 
  Network, ExternalLink, CheckCircle2, 
  HelpCircle, ArrowLeft, ArrowUpRight, Copy, Check, Briefcase, AlertCircle
} from 'lucide-react';
import { getPriorityColor, getStatusColor, truncateAddress, formatDate } from '../utils/format';

export default function AlertDetailPage() {
  const { id: rawId } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [caseModalOpen, setCaseModalOpen] = useState(false);
  const [caseTitle, setCaseTitle] = useState('');
  const [caseDescription, setCaseDescription] = useState('');
  const [copied, setCopied] = useState(false);

  // Clean identifier to handle raw IDs, prefixed IDs (#1, alert-1, lead-1)
  const cleanId = (rawId || '')
    .trim()
    .replace(/^alert[-_]/i, '')
    .replace(/^lead[-_]/i, '')
    .replace(/^#/, '');

  const { data: alert, isLoading, error, refetch } = useAlert(cleanId);
  const { data: explainData, isLoading: isExplainLoading } = useAlertExplain(cleanId);
  const { data: evidenceData } = useEvidenceList();
  const createCaseMutation = useCreateCase();

  if (isLoading) {
    return (
      <div className="space-y-5 max-w-6xl mx-auto p-2">
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-10 w-96" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Skeleton className="h-28 w-full" />
          <Skeleton className="h-28 w-full" />
          <Skeleton className="h-28 w-full" />
        </div>
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (error || !alert) {
    return (
      <div className="space-y-6 max-w-4xl mx-auto p-4">
        <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
          <Link to="/alerts" className="hover:text-slate-200 flex items-center gap-1 transition-colors">
            <ArrowLeft size={12} /> ALERTS QUEUE
          </Link>
          <span>/</span>
          <span className="text-slate-400">LEAD #{cleanId || 'UNKNOWN'}</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-lg p-8 flex flex-col items-center justify-center text-center">
          <div className="p-3 rounded-full bg-amber-500/10 text-amber-400 mb-3 border border-amber-500/20">
            <AlertCircle size={24} />
          </div>
          <h2 className="text-base font-mono font-bold text-white mb-1">
            Alert Record Not Located
          </h2>
          <p className="text-xs text-slate-400 max-w-md mb-6 leading-relaxed">
            Alert lead #{cleanId || rawId} does not match an existing alert in the platform database. It may have been resolved, archived, or purged.
          </p>

          <div className="flex items-center gap-3">
            <button
              onClick={() => refetch()}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-850 hover:bg-slate-800 border border-slate-700 text-xs font-mono text-slate-200 rounded transition cursor-pointer"
            >
              Retry Lookup
            </button>
            <Link
              to="/alerts"
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-mono font-medium rounded transition"
            >
              <ArrowLeft size={13} /> Return to Alerts Queue
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Safe normalized fields to guard against null/undefined values
  const priority = alert.priority || 'MEDIUM';
  const status = alert.status || 'NEW';
  const entityType = alert.entity_type || 'WALLET';
  const entityId = alert.entity_id || '';
  const anomalyScore = typeof alert.anomaly_score === 'number' 
    ? alert.anomaly_score 
    : parseFloat(String(alert.anomaly_score || 0)) || 0;
  const confidence = typeof alert.confidence === 'number' 
    ? alert.confidence 
    : parseFloat(String(alert.confidence || 0)) || 0;
  const modelVersion = alert.model_version || 'IF-2.0';

  const pColor = getPriorityColor(priority);
  const sColor = getStatusColor(status);

  const entityUrl = entityType === 'WALLET'
    ? `/wallets/${encodeURIComponent(entityId)}`
    : entityType === 'IP'
    ? `/ips/${encodeURIComponent(entityId)}`
    : `/transactions/${encodeURIComponent(entityId)}`;

  // Safe array extraction for evidence
  const rawEvidenceList: any[] = Array.isArray(evidenceData)
    ? evidenceData
    : Array.isArray(evidenceData?.items)
    ? evidenceData.items
    : [];

  const relatedEvidence = rawEvidenceList.filter(
    (e: any) => e && (
      (e.alert_id && String(e.alert_id) === String(alert.id)) || 
      (e.entity_id && String(e.entity_id) === String(entityId))
    )
  );

  // Safe normalized arrays for Explainability
  const contributingSignals: any[] = Array.isArray(explainData?.contributing_signals)
    ? explainData.contributing_signals
    : Array.isArray(explainData?.contributing_factors)
    ? explainData.contributing_factors
    : Array.isArray(alert.contributing_signals)
    ? alert.contributing_signals
    : typeof alert.contributing_signals === 'object' && alert.contributing_signals !== null
    ? Object.entries(alert.contributing_signals).map(([k, v]) => `${k}: ${v}`)
    : [];

  const recommendedActions: any[] = Array.isArray(explainData?.recommended_actions)
    ? explainData.recommended_actions
    : Array.isArray(explainData?.recommended_review_actions)
    ? explainData.recommended_review_actions
    : [
        `Trace counterparty interaction flows for ${entityType} ${truncateAddress(entityId)}`,
        'Correlate timestamp patterns with known suspicious temporal clusters',
        'Verify behavioral entropy against cluster baselines'
      ];

  const handleCopy = () => {
    if (!entityId) return;
    navigator.clipboard.writeText(entityId);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleCreateCase = async () => {
    if (!caseTitle) return;
    try {
      const res = await createCaseMutation.mutateAsync({
        title: caseTitle,
        description: caseDescription || `Investigation promoted from Alert #${alert.id} (${priority} priority on ${entityType} ${entityId})`,
        priority: priority,
        alert_id: alert.id,
      });
      setCaseModalOpen(false);
      navigate(`/cases/${res.id}`);
    } catch (err) {
      console.error('Failed to create case:', err);
    }
  };

  const scoreBarColor = 
    anomalyScore >= 75 ? 'bg-rose-500' :
    anomalyScore >= 50 ? 'bg-amber-500' : 'bg-blue-500';

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Navigation Breadcrumb */}
      <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
        <Link to="/alerts" className="hover:text-slate-200 flex items-center gap-1 transition-colors">
          <ArrowLeft size={12} /> ALERTS QUEUE
        </Link>
        <span>/</span>
        <span className="text-slate-300">LEAD #{alert.id}</span>
      </div>

      {/* Main Alert Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-sm">
        <div>
          <div className="flex flex-wrap items-center gap-2.5 mb-1.5">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">Alert Lead #{alert.id}</span>
            <span className={`inline-flex px-2 py-0.5 rounded text-[10px] font-mono font-bold ${pColor.bg} ${pColor.text} border ${pColor.border}`}>
              {priority}
            </span>
            <span className={`inline-flex px-2 py-0.5 rounded text-[10px] font-mono ${sColor.bg} ${sColor.text} border ${sColor.border}`}>
              {status}
            </span>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-850 text-slate-400 border border-slate-750">
              {entityType}
            </span>
          </div>

          <div className="flex items-center gap-2 mt-1">
            <h1 className="text-base sm:text-lg font-mono font-bold text-white break-all">
              {entityId || 'Unspecified Entity'}
            </h1>
            {entityId && (
              <button
                onClick={handleCopy}
                className="p-1 text-slate-400 hover:text-slate-200 rounded hover:bg-slate-800 transition-colors cursor-pointer"
                title="Copy identifier"
                aria-label="Copy identifier"
              >
                {copied ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
              </button>
            )}
          </div>

          <div className="text-[11px] text-slate-400 mt-1 font-mono">
            Triggered {formatDate(alert.created_at)} • Model: <span className="text-slate-300">{modelVersion}</span>
          </div>
        </div>

        {/* Primary Action Buttons */}
        <div className="flex items-center gap-2 shrink-0">
          <Link
            to={`/graph?entityType=${entityType}&entityId=${encodeURIComponent(entityId)}`}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-850 hover:bg-slate-800 text-slate-200 text-xs font-mono font-medium rounded border border-slate-750 transition-colors"
          >
            <Network size={13} className="text-cyan-400" /> Graph Traversal
          </Link>
          <button
            onClick={() => {
              setCaseTitle(`Investigate ${entityType} ${truncateAddress(entityId)}`);
              setCaseModalOpen(true);
            }}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium rounded transition shadow-xs cursor-pointer"
          >
            <Briefcase size={13} /> Promote to Case
          </button>
        </div>
      </div>

      {/* Analytical Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded p-4">
          <div className="text-[11px] font-mono uppercase tracking-wider text-slate-400">Anomaly Dispersion Score</div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-2xl font-bold font-mono text-white">
              {anomalyScore.toFixed(1)}
            </span>
            <span className="text-xs font-mono text-slate-500">/ 100</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded overflow-hidden mt-3">
            <div 
              className={`h-full ${scoreBarColor}`} 
              style={{ width: `${Math.min(anomalyScore, 100)}%` }}
            />
          </div>
          <div className="text-[10px] text-slate-500 font-mono mt-2">
            Isolation Forest empirical quantile
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded p-4">
          <div className="text-[11px] font-mono uppercase tracking-wider text-slate-400">Evidence Sufficiency</div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-2xl font-bold font-mono text-white">
              {Math.round(confidence * 100)}%
            </span>
            <span className="text-xs font-mono text-emerald-400">
              {confidence > 0.7 ? 'High Sufficiency' : 'Moderate'}
            </span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded overflow-hidden mt-3">
            <div 
              className="h-full bg-emerald-500" 
              style={{ width: `${Math.min(confidence * 100, 100)}%` }}
            />
          </div>
          <div className="text-[10px] text-slate-500 font-mono mt-2">
            Multi-observation convergence ratio
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded p-4">
          <div className="text-[11px] font-mono uppercase tracking-wider text-slate-400">Entity Dossier Target</div>
          <div className="mt-1.5">
            <Link to={entityUrl} className="text-xs font-mono text-blue-400 hover:underline inline-flex items-center gap-1">
              {truncateAddress(entityId, 12, 10)}
              <ArrowUpRight size={12} />
            </Link>
            <div className="text-[11px] text-slate-400 mt-1">
              Category: <span className="font-mono text-slate-300">{entityType}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Why It Was Flagged (Analytical Explainability) */}
      <div className="bg-slate-900 border border-slate-800 rounded p-5 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div>
            <h2 className="text-xs font-mono font-semibold uppercase tracking-wider text-slate-200">
              Forensic Assessment & Feature Explainability
            </h2>
            <p className="text-[11px] text-slate-400 mt-0.5">Quantitative signal contribution and mathematical rationale</p>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-850 text-slate-400 border border-slate-750">
            DETERMINISTIC EVALUATION
          </span>
        </div>

        {isExplainLoading ? (
          <div className="space-y-2 py-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
          </div>
        ) : (
          <div className="space-y-4 text-xs">
            {/* Primary Finding Summary */}
            <div className="bg-slate-850 p-3.5 rounded border border-slate-800 text-slate-200 leading-relaxed font-mono text-[11px]">
              {explainData?.primary_findings || explainData?.summary || `Behavioral anomaly evaluation active on ${entityType} ${truncateAddress(entityId)}.`}
            </div>

            {/* Contributing Signals & Features */}
            {contributingSignals.length > 0 && (
              <div className="space-y-2">
                <h3 className="text-[11px] font-mono uppercase tracking-wider text-slate-300">
                  Primary Contributing Features & Signals
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {contributingSignals.map((sig: any, idx: number) => (
                    <div key={idx} className="p-2.5 bg-slate-850 rounded border border-slate-800 text-slate-300 flex items-start gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 shrink-0" />
                      <span className="text-[11px] font-mono leading-relaxed">
                        {typeof sig === 'string' ? sig : JSON.stringify(sig)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommended Review Actions */}
            {recommendedActions.length > 0 && (
              <div className="space-y-2 pt-2">
                <h3 className="text-[11px] font-mono uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                  <CheckCircle2 size={13} className="text-emerald-500" /> Recommended Verification Actions
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {recommendedActions.map((act: any, idx: number) => (
                    <div key={idx} className="p-2.5 bg-slate-850 rounded border border-slate-800 text-slate-300 flex items-start gap-2">
                      <span className="text-slate-500 font-mono text-[10px] mt-0.5">{idx + 1}.</span>
                      <span className="text-[11px] leading-relaxed">
                        {typeof act === 'string' ? act : JSON.stringify(act)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Uncertainty / Caveats */}
            {explainData?.uncertainty_caveats && (
              <div className="p-2.5 bg-slate-850/60 rounded border border-slate-800 text-[11px] text-slate-400 flex items-center gap-2">
                <HelpCircle size={13} className="text-slate-500 shrink-0" />
                <span>Assessment Caveat: {String(explainData.uncertainty_caveats)}</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Supporting Evidence Lineage */}
      <div className="bg-slate-900 border border-slate-800 rounded p-5 space-y-3">
        <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
          <h2 className="text-xs font-mono font-semibold uppercase tracking-wider text-slate-200">
            Supporting Forensic Evidence ({relatedEvidence.length})
          </h2>
          <Link to="/evidence" className="text-[11px] font-mono text-blue-500 hover:text-blue-400">
            View Immutable Chain <ExternalLink size={11} className="inline ml-0.5" />
          </Link>
        </div>

        {relatedEvidence.length > 0 ? (
          <div className="divide-y divide-slate-800">
            {relatedEvidence.slice(0, 5).map((ev: any) => (
              <div key={ev.id} className="py-2.5 flex items-center justify-between text-xs">
                <div>
                  <div className="font-mono text-slate-300 text-[11px]">
                    {ev.observation || ev.description || 'Forensic signal observation'}
                  </div>
                  <div className="text-[10px] font-mono text-slate-500 mt-0.5">
                    Hash: {ev.evidence_hash ? truncateAddress(ev.evidence_hash, 16, 12) : 'Unchained'}
                  </div>
                </div>
                <span className="text-[10px] font-mono text-slate-400">
                  {formatDate(ev.created_at)}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-xs text-slate-500 font-mono py-3">
            No direct evidence entries linked yet. Promote to Case to attach evidence artefacts.
          </div>
        )}
      </div>

      {/* Case Promotion Modal */}
      {caseModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded p-5 w-full max-w-md space-y-4 shadow-2xl">
            <div>
              <h3 className="text-sm font-mono font-bold text-white uppercase tracking-wider">
                Promote to Investigative Case
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Create a persistent investigative dossier with linked evidence and notes.
              </p>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">CASE TITLE</label>
                <input
                  type="text"
                  value={caseTitle}
                  onChange={(e) => setCaseTitle(e.target.value)}
                  className="w-full px-3 py-1.5 bg-slate-950 border border-slate-800 rounded text-slate-200 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">INVESTIGATIVE HYPOTHESIS</label>
                <textarea
                  rows={3}
                  value={caseDescription}
                  onChange={(e) => setCaseDescription(e.target.value)}
                  placeholder="Record initial hypothesis, forensic rationale, and targets..."
                  className="w-full px-3 py-1.5 bg-slate-950 border border-slate-800 rounded text-slate-200 focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-800">
              <button
                type="button"
                onClick={() => setCaseModalOpen(false)}
                className="px-3 py-1.5 bg-slate-850 hover:bg-slate-800 text-slate-300 text-xs font-mono rounded border border-slate-750 transition cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleCreateCase}
                disabled={!caseTitle || createCaseMutation.isPending}
                className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded transition cursor-pointer"
              >
                {createCaseMutation.isPending ? 'Creating...' : 'Confirm Case Promotion'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
