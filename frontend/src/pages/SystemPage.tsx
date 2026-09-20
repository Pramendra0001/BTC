import { PageHeader } from '../components/ui/PageHeader';

export default function SystemPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="System" />
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
        <p className="text-slate-400">Content for SystemPage will be displayed here.</p>
      </div>
    </div>
  );
}
