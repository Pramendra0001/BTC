
export const StatCard = ({ icon, label, value, trend }: any) => {
  return (
    <div className="bg-slate-900 p-4 rounded-lg border border-slate-800">
      <div className="flex items-center space-x-2 text-slate-400 mb-2">
        {icon}
        <span className="text-sm">{label}</span>
      </div>
      <div className="text-2xl font-bold">{value}</div>
      {trend && <div className="text-xs text-emerald-500 mt-1">{trend}</div>}
    </div>
  );
}
