import React from 'react';

interface Column<T = any> {
  header: string;
  accessorKey?: string;
  cell?: (row: T) => React.ReactNode;
  className?: string;
}

interface DataTableProps<T = any> {
  columns: Column<T>[];
  data: T[];
  emptyMessage?: string;
}

export const DataTable = <T extends Record<string, any>>({ 
  columns, 
  data, 
  emptyMessage = "No records found." 
}: DataTableProps<T>) => {
  return (
    <div className="overflow-x-auto w-full border border-slate-800 rounded bg-slate-900">
      <table className="w-full text-left text-xs border-collapse">
        <thead className="bg-slate-850 text-slate-400 border-b border-slate-800 font-mono text-[11px] uppercase tracking-wider">
          <tr>
            {columns.map((c, i) => (
              <th key={i} className={`px-3.5 py-2.5 font-medium ${c.className || ''}`}>
                {c.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/60">
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-4 py-8 text-center text-slate-500 font-mono text-xs">
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((row, i) => (
              <tr key={i} className="hover:bg-slate-850/50 transition-colors">
                {columns.map((c, j) => (
                  <td key={j} className={`px-3.5 py-2.5 text-slate-300 ${c.className || ''}`}>
                    {c.cell ? c.cell(row) : (c.accessorKey ? row[c.accessorKey] : null)}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};
