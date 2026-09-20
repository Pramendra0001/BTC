import { useState, useRef } from 'react';
import { useDatasets, useUploadDataset, useRunPipeline } from '../api/hooks';
import { PageHeader } from '../components/ui/PageHeader';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { 
  Database, Upload, Play, CheckCircle2, AlertCircle, 
  FileText, ArrowRight, RefreshCw, Cpu, ShieldAlert 
} from 'lucide-react';
import { formatDate, formatNumber } from '../utils/format';

export default function DatasetsPage() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [processingId, setProcessingId] = useState<number | null>(null);
  const [pipelineMessage, setPipelineMessage] = useState<string | null>(null);

  const { data, isLoading, error, refetch } = useDatasets();
  const uploadMutation = useUploadDataset();
  const runPipelineMutation = useRunPipeline();

  const datasets = data?.datasets || [];

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      await uploadMutation.mutateAsync(formData);
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err) {
      console.error('Upload failed:', err);
    }
  };

  const handleRunPipeline = async (datasetId: number) => {
    setProcessingId(datasetId);
    setPipelineMessage(null);
    try {
      const res = await runPipelineMutation.mutateAsync(datasetId);
      setPipelineMessage(
        `Intelligence Pipeline Complete: ${res.evidence_count || 0} evidence signals & ${res.alert_count || 0} prioritized alerts generated!`
      );
      refetch();
    } catch (err) {
      console.error('Pipeline execution failed:', err);
      setPipelineMessage('Pipeline execution failed. Check server logs.');
    } finally {
      setProcessingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Dataset Management & Ingestion" 
        description="Ingest bulk Bitcoin transaction metadata and network observations in CSV, JSON, or XML formats" 
      />

      {/* Upload Box */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg">
        <h2 className="text-sm font-semibold text-white mb-2 flex items-center gap-2">
          <Upload size={16} className="text-blue-400" />
          Upload New Dataset
        </h2>
        <p className="text-xs text-slate-400 mb-4">
          Accepts CSV, JSON, or XML files containing transaction hashes, inputs, outputs, timestamps, IP addresses, ASNs, and countries.
        </p>

        <div className="flex flex-col sm:flex-row items-center gap-4">
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,.json,.xml"
            onChange={handleFileChange}
            className="block w-full text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-500 cursor-pointer bg-slate-950 border border-slate-800 rounded-lg p-1"
          />

          <button
            onClick={handleUpload}
            disabled={!selectedFile || uploadMutation.isPending}
            className="w-full sm:w-auto px-5 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition shrink-0 flex items-center justify-center gap-2 shadow"
          >
            {uploadMutation.isPending ? (
              <>
                <RefreshCw size={14} className="animate-spin" /> Ingesting & Validating...
              </>
            ) : (
              <>
                <Upload size={14} /> Upload Dataset
              </>
            )}
          </button>
        </div>

        {uploadMutation.isSuccess && (
          <div className="mt-3 p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-400 flex items-center gap-2">
            <CheckCircle2 size={14} /> Dataset successfully uploaded, parsed, and validated!
          </div>
        )}
      </div>

      {/* Pipeline Status Banner */}
      {pipelineMessage && (
        <div className="p-4 rounded-xl bg-blue-600/10 border border-blue-500/30 text-xs text-blue-300 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Cpu size={16} className="text-blue-400 shrink-0" />
            <span>{pipelineMessage}</span>
          </div>
          <button onClick={() => setPipelineMessage(null)} className="text-slate-400 hover:text-white text-xs">
            Dismiss
          </button>
        </div>
      )}

      {/* Datasets Table */}
      {isLoading ? (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
        </div>
      ) : error ? (
        <ErrorState message="Failed to load datasets." onRetry={() => refetch()} />
      ) : datasets.length === 0 ? (
        <EmptyState
          icon={<Database size={32} />}
          title="No Datasets Uploaded"
          description="Upload a CSV, JSON, or XML file to initiate analysis. You can also generate deterministic test scenarios using the synthetic generator."
        />
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/70 text-slate-400 border-b border-slate-800 font-mono text-[11px] uppercase">
                <tr>
                  <th className="py-3 px-4">Dataset Name</th>
                  <th className="py-3 px-4">Format</th>
                  <th className="py-3 px-4">Total Records</th>
                  <th className="py-3 px-4">Valid Records</th>
                  <th className="py-3 px-4">Quality / Duplicates</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Ingested At</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {datasets.map((ds: any) => {
                  const isProcessing = processingId === ds.id || ds.status === 'PROCESSING_PIPELINE';
                  return (
                    <tr key={ds.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-3 px-4 font-bold text-white">
                        {ds.name}
                      </td>
                      <td className="py-3 px-4 text-slate-300 uppercase">
                        {ds.format || 'csv'}
                      </td>
                      <td className="py-3 px-4 text-slate-200">
                        {formatNumber(ds.total_records)}
                      </td>
                      <td className="py-3 px-4 text-emerald-400">
                        {formatNumber(ds.valid_records)}
                      </td>
                      <td className="py-3 px-4 text-slate-400 text-[11px]">
                        {ds.duplicate_records || 0} duplicates ({ds.invalid_records || 0} rejected)
                      </td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-0.5 rounded text-[10px] ${
                          ds.status === 'COMPLETED' || ds.status === 'PIPELINE_COMPLETE'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                            : ds.status === 'PROCESSING_PIPELINE'
                            ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30 animate-pulse'
                            : 'bg-slate-800 text-slate-300 border border-slate-700'
                        }`}>
                          {ds.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-400 text-[11px]">
                        {formatDate(ds.created_at)}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => handleRunPipeline(ds.id)}
                          disabled={isProcessing}
                          className="inline-flex items-center gap-1.5 px-3 py-1 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-sans font-medium rounded-lg transition shadow"
                        >
                          {isProcessing ? (
                            <>
                              <RefreshCw size={12} className="animate-spin" /> Analyzing...
                            </>
                          ) : (
                            <>
                              <Play size={12} /> Run ML Pipeline
                            </>
                          )}
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
