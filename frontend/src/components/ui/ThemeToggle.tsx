import { useTheme, type ThemePreference } from '../../context/ThemeContext';
import { Sun, Moon, Monitor } from 'lucide-react';

export function ThemeToggle() {
  const { theme, resolvedTheme, setTheme } = useTheme();

  const options: Array<{ value: ThemePreference; label: string; icon: typeof Sun }> = [
    { value: 'light', label: 'Light', icon: Sun },
    { value: 'dark', label: 'Dark', icon: Moon },
    { value: 'system', label: 'System', icon: Monitor },
  ];

  return (
    <div className="flex items-center bg-slate-950/80 border border-slate-800 rounded-lg p-0.5 shadow-inner">
      {options.map((opt) => {
        const Icon = opt.icon;
        const isSelected = theme === opt.value;
        return (
          <button
            key={opt.value}
            type="button"
            onClick={() => setTheme(opt.value)}
            title={`Switch to ${opt.label} theme (Active: ${resolvedTheme})`}
            aria-label={`Switch to ${opt.label} theme`}
            className={`flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium transition-all cursor-pointer ${
              isSelected
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
            }`}
          >
            <Icon size={13} className={isSelected ? 'text-white' : 'text-slate-400'} />
            <span className="hidden sm:inline text-[11px] font-mono">{opt.label}</span>
          </button>
        );
      })}
    </div>
  );
}
