
export const TimelineView = ({ events }: { events: any[] }) => {
  return (
    <div className="space-y-4">
      {events?.map((e, i) => (
         <div key={i} className="flex gap-4">
            <div className="w-1 bg-slate-700 h-full relative" />
            <div className="bg-slate-900 p-4 rounded border border-slate-800 flex-1">{e.title}</div>
         </div>
      ))}
    </div>
  );
}
