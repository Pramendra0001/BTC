export const EmptyState = ({ icon, message, action }: any) => {
  return (
    <div className="p-8 flex flex-col items-center justify-center text-center text-slate-400 border border-dashed border-slate-800 rounded-lg">
      <div className="mb-4 opacity-50">{icon}</div>
      <div className="mb-4">{message}</div>
      {action}
    </div>
  );
}
