import React from 'react';

interface StatCardProps {
  icon?: React.ReactNode;
  label: string;
  value: string | number;
  subtext?: string;
  trend?: string;
}

export const StatCard = ({ icon, label, value, subtext, trend }: StatCardProps) => {
  return (
    <div className="bg-slate-900 p-4 rounded border border-slate-800 flex flex-col justify-between hover:border-slate-700 transition-colors">
      <div className="flex items-center justify-between mb-2">
        <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400">{label}</span>
        {icon && <span className="text-slate-500">{icon}</span>}
      </div>
      <div>
        <div className="text-2xl font-bold font-mono text-white tracking-tight">{value}</div>
        {subtext && <div className="text-[11px] text-slate-500 mt-1">{subtext}</div>}
        {trend && <div className="text-[11px] font-mono text-emerald-500 mt-1">{trend}</div>}
      </div>
    </div>
  );
};
