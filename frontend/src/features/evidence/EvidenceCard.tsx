
export const EvidenceCard = ({ evidence }: { evidence: any }) => {
  return (
    <div className="bg-slate-900 p-4 rounded border border-slate-800">
      <h4 className="font-semibold">{evidence?.title || "Evidence"}</h4>
      <p className="text-sm text-slate-400">{evidence?.description || "Description"}</p>
    </div>
  );
}
