import {
  Database, ShieldCheck, Filter, Trophy, ChevronRight, ArrowUpRight,
} from "lucide-react";

// Discovery funnel: how 100k candidates narrow down to the Top 100.
export default function PipelinePanel({ stats, onShowTrap, onShowTop10 }) {
  if (!stats || !stats.total_scanned) return null;

  const scanned = stats.total_scanned;
  const honeypots = stats.honeypots_detected || 0;
  const softPenalized = stats.soft_penalized || 0;
  const topK = stats.top_k || 100;

  const genuine = scanned - honeypots;
  const clean = Math.max(genuine - softPenalized, 0);

  const stages = [
    {
      icon: Database,
      value: scanned,
      label: "Profiles scanned",
      note: "full candidate pool",
      accent: "text-brand-300 bg-brand-600/20",
      bar: "bg-brand-500",
    },
    {
      icon: ShieldCheck,
      value: genuine,
      label: "Passed integrity",
      note: `${honeypots} honeypots removed`,
      accent: "text-emerald-300 bg-emerald-600/20",
      bar: "bg-emerald-500",
      onClick: onShowTrap,
      hint: "See the integrity & trap detection breakdown",
    },
    {
      icon: Filter,
      value: clean,
      label: "Clean of red flags",
      note: `${softPenalized.toLocaleString()} down-ranked`,
      accent: "text-amber-300 bg-amber-600/20",
      bar: "bg-amber-500",
      onClick: onShowTrap,
      hint: "See which red-flag patterns were penalized",
    },
    {
      icon: Trophy,
      value: topK,
      display: "Top 10",
      label: "Top shortlist",
      note: "surfaced for review",
      accent: "text-fuchsia-300 bg-fuchsia-600/20",
      bar: "bg-fuchsia-500",
      onClick: onShowTop10,
      hint: "Jump to the Top 10 shortlist",
    },
  ];

  const pct = (v) => Math.max((v / scanned) * 100, 4); // min width so the last bar is visible

  return (
    <div className="card p-5">
      <h3 className="font-semibold text-slate-200">Candidate Discovery Pipeline</h3>
      <p className="text-xs text-slate-500 mb-4">
        From {scanned.toLocaleString()} raw profiles to the {topK} strongest matches —
        impossible profiles disqualified, red-flag profiles down-ranked, the best surfaced.
      </p>

      <div className="flex flex-col lg:flex-row items-stretch gap-2">
        {stages.map((s, i) => {
          const Icon = s.icon;
          const clickable = typeof s.onClick === "function";
          const Tile = clickable ? "button" : "div";
          return (
            <div key={s.label} className="flex items-stretch gap-2 flex-1">
              <Tile
                onClick={s.onClick}
                title={s.hint}
                className={`flex-1 text-left w-full rounded-xl bg-slate-900/60 border border-slate-800 p-4 relative ${
                  clickable
                    ? "cursor-pointer transition hover:-translate-y-0.5 hover:ring-1 hover:ring-brand-500/60 group"
                    : ""
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <div className={`p-1.5 rounded-lg ${s.accent}`}>
                    <Icon size={16} />
                  </div>
                  <span className="text-xs text-slate-400">{s.label}</span>
                </div>
                <div className="text-2xl font-bold leading-none">
                  {s.display ?? s.value.toLocaleString()}
                </div>
                <div className="text-[11px] text-slate-500 mt-1">{s.note}</div>
                <div className="mt-3 h-1.5 rounded-full bg-slate-800 overflow-hidden">
                  <div className={`h-full ${s.bar}`} style={{ width: `${pct(s.value)}%` }} />
                </div>
                {clickable && (
                  <ArrowUpRight
                    size={15}
                    className="absolute top-3 right-3 text-slate-600 group-hover:text-brand-400 transition"
                  />
                )}
              </Tile>
              {i < stages.length - 1 && (
                <div className="hidden lg:flex items-center text-slate-600">
                  <ChevronRight size={18} />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
