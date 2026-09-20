import { Link } from 'react-router-dom';
import { PageHeader } from '../components/ui/PageHeader';
import { Lock, EyeOff, ArrowLeft } from 'lucide-react';

export default function PrivacyPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
        <Link to="/" className="hover:text-slate-200 flex items-center gap-1">
          <ArrowLeft size={12} /> Command Center
        </Link>
        <span>/</span>
        <span className="text-slate-300">Privacy Policy</span>
      </div>

      <PageHeader
        title="Privacy & Data Protection Policy"
        description="Data governance, handling of forensic telemetry, and retention standards"
        actions={
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-amber-500/10 border border-amber-500/30 text-amber-500 text-xs font-mono font-medium">
            DRAFT FOR REVIEW
          </div>
        }
      />

      <div className="bg-slate-900 border border-slate-800 rounded-lg p-6 space-y-6 text-sm leading-relaxed text-slate-300">
        <div className="p-3 bg-slate-850 border border-slate-800 rounded text-xs text-slate-400 font-mono">
          STATUS: Draft Document • Zero Third-Party Telemetry Commitment • Version 1.0
        </div>

        <section className="space-y-2">
          <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
            <EyeOff size={18} className="text-emerald-500" />
            1. Zero Third-Party Telemetry & Tracking
          </h2>
          <p>
            BTC-SHIELD contains zero third-party tracking scripts, analytics beacons, marketing pixels, or external CDN dependencies at runtime. All assets, scripts, and stylesheets are self-hosted and bundled locally.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
            <Lock size={18} className="text-blue-500" />
            2. Authentication & Credential Storage
          </h2>
          <p>
            User credentials are protected using industry-standard bcrypt one-way hashing with salt. Session tokens use signed JSON Web Tokens (JWT) stored strictly in client-side secure browser storage. Tokens are not transmitted to any server other than the configured backend endpoint.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-semibold text-slate-100">
            3. Ingested Data Retention & Processing
          </h2>
          <p>
            Ingested data (transaction hashes, wallet addresses, IP addresses, ASN numbers) is stored exclusively in the designated database (local SQLite or PostgreSQL). In air-gapped mode, data never leaves the local filesystem or host container.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-base font-semibold text-slate-100">
            4. Auditability & Immutable Action Logs
          </h2>
          <p className="text-slate-400 text-xs">
            All user operations (logins, queries, case modifications, dataset uploads) are recorded in the internal append-only audit log for forensic accountability.
          </p>
        </section>
      </div>
    </div>
  );
}
