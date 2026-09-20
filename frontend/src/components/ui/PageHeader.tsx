export const PageHeader = ({ title, description, actions }: any) => {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6">
      <div>
        <h1 className="text-2xl font-bold text-white">{title}</h1>
        {description && <p className="text-slate-400 text-sm mt-1">{description}</p>}
      </div>
      {actions && <div className="mt-4 sm:mt-0 flex gap-2">{actions}</div>}
    </div>
  );
}
