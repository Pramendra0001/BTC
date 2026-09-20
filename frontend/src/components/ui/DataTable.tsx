export const DataTable = ({ columns, data }: { columns: any[], data: any[] }) => {
  return (
    <div className="overflow-x-auto w-full border border-slate-800 rounded-lg">
      <table className="w-full text-left text-sm">
        <thead className="bg-slate-900 text-slate-400">
          <tr>
            {columns.map((c, i) => (
              <th key={i} className="px-4 py-3 border-b border-slate-800">{c.header}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800 bg-slate-900/50">
          {data.map((row, i) => (
            <tr key={i} className="hover:bg-slate-800 transition">
              {columns.map((c, j) => (
                <td key={j} className="px-4 py-3">{c.cell ? c.cell(row) : row[c.accessorKey]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
