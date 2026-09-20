import React, { useState } from 'react';
import { useDataQualitySummary, useRejectedRecords } from '../api/hooks';
import { PageHeader } from '../components/ui/PageHeader';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { ShieldCheck, AlertOctagon, FileCheck, Copy, Globe, Server, CheckCircle2, ChevronRight, XCircle } from 'lucide-react';
import { formatNumber } from '../utils/format';

export default function DataQualityPage() {
  const [selectedDatasetId, setSelectedDatasetId] = useState<number | undefined>(undefined);
  const [expandedRecord, setExpandedRecord] = useState<number | null>(null);

  const { data: summary, isLoading: summaryLoading, error: summaryError } = useDataQualitySummary();
  const { data: rejected, isLoading: rejectedLoading, error: rejectedError } = useRejectedRecords({
    dataset_id: selectedDatasetId,
    limit: 50,
    offset: 0
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Data Quality & Ingestion Quarantine Center"
        description="Multi-format schema validation, quarantine tracking for malformed records, and network telemetry enrichment audits"
      />

      {/* KPI Overview */}
      {summaryLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-slate-900 border border-slate-800 rounded-xl p-4">
              <Skeleton className="h-4 w-24 mb-2" />
              <Skeleton className="h-7 w-16" />
            </div>
          ))}
        </div>
      ) : summaryError ? (
        <ErrorState message="Failed to load data quality summary" />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
              <span>Overall Data Health</span>
              <ShieldCheck size={16} className="text-emerald-400" />
            </div>
            <div className="text-2xl font-bold text-emerald-400 font-mono">
              {summary?.overall_health_score || 100}%
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              Valid: {formatNumber(summary?.valid_records || 0)} / {formatNumber(summary?.total_records || 0)}
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
              <span>Quarantined Records</span>
              <AlertOctagon size={16} className="text-rose-400" />
            </div>
            <div className="text-2xl font-bold text-rose-400 font-mono">
              {formatNumber(summary?.invalid_records || 0)}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              Isolated without crashing pipeline
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
              <span>Duplicate Records</span>
              <Copy size={16} className="text-amber-400" />
            </div>
            <div className="text-2xl font-bold text-amber-400 font-mono">
              {formatNumber(summary?.duplicate_records || 0)}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              Deduplicated at ingestion layer
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
              <span>Datasets Audited</span>
              <FileCheck size={16} className="text-blue-400" />
            </div>
            <div className="text-2xl font-bold text-white font-mono">
              {summary?.total_datasets || 0}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              Multi-format: CSV, JSON, XML
            </div>
          </div>
        </div>
      )}

      {/* Enrichment Coverage Section */}
      {summary && summary.enrichment_coverage && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Globe size={16} className="text-blue-400" />
              Network Telemetry & Correlation Coverage
            </h3>
            <span className="text-xs font-mono text-slate-400">
              Total Observations: {formatNumber(summary.enrichment_coverage.network_observations_total)}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-slate-950/60 p-4 rounded-lg border border-slate-800/80 space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-slate-400">GeoIP Resolution</span>
                <span className="font-mono text-emerald-400 font-bold">{summary.enrichment_coverage.geoip_resolution_pct}%</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-emerald-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${summary.enrichment_coverage.geoip_resolution_pct}%` }}
                />
              </div>
              <p className="text-[10px] text-slate-500">ISO Country code mapped from IP telemetry</p>
            </div>

            <div className="bg-slate-950/60 p-4 rounded-lg border border-slate-800/80 space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-slate-400">ASN Resolution</span>
                <span className="font-mono text-blue-400 font-bold">{summary.enrichment_coverage.asn_resolution_pct}%</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${summary.enrichment_coverage.asn_resolution_pct}%` }}
                />
              </div>
              <p className="text-[10px] text-slate-500">Autonomous System Number associated with node IP</p>
            </div>

            <div className="bg-slate-950/60 p-4 rounded-lg border border-slate-800/80 space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-slate-400">TX-Network Correlation</span>
                <span className="font-mono text-purple-400 font-bold">{summary.enrichment_coverage.tx_network_correlation_pct}%</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-purple-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${summary.enrichment_coverage.tx_network_correlation_pct}%` }}
                />
              </div>
              <p className="text-[10px] text-slate-500">Transactions linked to real-time network observations</p>
            </div>
          </div>
        </div>
      )}

      {/* Datasets Quality Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
            Dataset Ingestion Quality Breakdown
          </h3>
          <span className="text-xs text-slate-400">
            Click dataset to filter quarantined records
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider bg-slate-950/40">
                <th className="p-3">Dataset Name</th>
                <th className="p-3">Format</th>
                <th className="p-3">Total Records</th>
                <th className="p-3">Valid</th>
                <th className="p-3">Invalid</th>
                <th className="p-3">Duplicates</th>
                <th className="p-3">Health Score</th>
                <th className="p-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {summary?.datasets?.map((ds: any) => (
                <tr
                  key={ds.id}
                  onClick={() => setSelectedDatasetId(selectedDatasetId === ds.id ? undefined : ds.id)}
                  className={`hover:bg-slate-800/40 transition-colors cursor-pointer ${
                    selectedDatasetId === ds.id ? 'bg-blue-500/10' : ''
                  }`}
                >
                  <td className="p-3 font-medium text-white flex items-center gap-2">
                    <FileCheck size={14} className="text-slate-400" />
                    {ds.name}
                  </td>
                  <td className="p-3">
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300">
                      {ds.format}
                    </span>
                  </td>
                  <td className="p-3 font-mono">{formatNumber(ds.total_records)}</td>
                  <td className="p-3 font-mono text-emerald-400">{formatNumber(ds.valid_records)}</td>
                  <td className="p-3 font-mono text-rose-400">{formatNumber(ds.invalid_records)}</td>
                  <td className="p-3 font-mono text-amber-400">{formatNumber(ds.duplicate_records)}</td>
                  <td className="p-3 font-mono font-bold text-emerald-400">{ds.health_score}%</td>
                  <td className="p-3">
                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/20 text-emerald-400">
                      {ds.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Quarantined Records Viewer */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
            <AlertOctagon size={16} className="text-rose-400" />
            Quarantined & Malformed Records {selectedDatasetId ? `(Dataset #${selectedDatasetId})` : ''}
          </h3>
          {selectedDatasetId && (
            <button
              onClick={() => setSelectedDatasetId(undefined)}
              className="text-xs text-blue-400 hover:underline"
            >
              Clear filter (Show all)
            </button>
          )}
        </div>

        {rejectedLoading ? (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-10 w-full" />
          </div>
        ) : rejectedError ? (
          <ErrorState message="Failed to load rejected records" />
        ) : !rejected?.rejected_records || rejected.rejected_records.length === 0 ? (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center space-y-2">
            <CheckCircle2 size={36} className="text-emerald-400 mx-auto" />
            <h4 className="text-sm font-bold text-white">Zero Malformed Records Quarantined</h4>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              All records passed strict schema validation and normalization without error.
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {rejected.rejected_records.map((r: any) => {
              const isExpanded = expandedRecord === r.id;
              return (
                <div
                  key={r.id}
                  className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden hover:border-slate-700 transition-colors"
                >
                  <div
                    onClick={() => setExpandedRecord(isExpanded ? null : r.id)}
                    className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-3 cursor-pointer"
                  >
                    <div className="flex items-center gap-3">
                      <XCircle size={18} className="text-rose-400 flex-shrink-0" />
                      <div>
                        <div className="text-xs font-bold text-white flex items-center gap-2">
                          <span>Line #{r.line_number}</span>
                          <span className="text-slate-500">•</span>
                          <span className="text-rose-400 font-mono">{r.error_message}</span>
                        </div>
                        <div className="text-[11px] text-slate-500 mt-0.5">
                          Dataset #{r.dataset_id} • Quarantined at {r.created_at}
                        </div>
                      </div>
                    </div>
                    <ChevronRight
                      size={18}
                      className={`text-slate-400 transition-transform ${isExpanded ? 'rotate-90 text-rose-400' : ''}`}
                    />
                  </div>

                  {isExpanded && (
                    <div className="border-t border-slate-800 p-4 bg-slate-950/80">
                      <div className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">
                        Raw Quarantined Payload (Immutable):
                      </div>
                      <pre className="text-[11px] font-mono text-slate-300 bg-slate-900 p-3 rounded-lg overflow-x-auto border border-slate-800">
                        {JSON.stringify(r.raw_data, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
