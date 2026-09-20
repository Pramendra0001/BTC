import React from 'react';

interface EmptyStateProps {
  icon?: React.ReactNode;
  title?: string;
  description?: string;
  message?: string;
  action?: React.ReactNode;
}

export const EmptyState = ({ icon, title, description, message, action }: EmptyStateProps) => {
  const displayTitle = title || "No Records Found";
  const displayDesc = description || message || "No data is currently available for this investigative view.";

  return (
    <div className="p-8 sm:p-12 flex flex-col items-center justify-center text-center bg-slate-900 border border-slate-800 rounded">
      {icon && <div className="mb-3 text-slate-500">{icon}</div>}
      <h3 className="text-sm font-semibold text-slate-200 mb-1">{displayTitle}</h3>
      <p className="text-xs text-slate-400 max-w-md mb-4 leading-relaxed">{displayDesc}</p>
      {action && <div>{action}</div>}
    </div>
  );
};
