import { useNavigate } from "react-router-dom";
import { Users, Gauge, Trophy, CheckCircle2, ShieldAlert, ArrowUpRight } from "lucide-react";

const ICONS = {
  total: Users,
  avg: Gauge,
  top: Trophy,
  skills: CheckCircle2,
  honeypot: ShieldAlert,
};

function Card({ icon, label, value, sub, accent, onClick, hint }) {
  const Icon = ICONS[icon] || Users;
  const clickable = typeof onClick === "function";
  const Comp = clickable ? "button" : "div";
  return (
    <Comp
      onClick={onClick}
      title={hint}
      className={`card p-5 flex items-center gap-4 text-left w-full relative ${
        clickable
          ? "cursor-pointer transition hover:-translate-y-0.5 hover:ring-1 hover:ring-brand-500/60 group"
          : ""
      }`}
    >
      <div className={`p-3 rounded-xl ${accent}`}>
        <Icon size={22} />
      </div>
      <div className="min-w-0">
        <div className="text-slate-400 text-sm">{label}</div>
        <div className="text-2xl font-bold truncate">{value}</div>
        {sub && <div className="text-xs text-slate-500 truncate">{sub}</div>}
      </div>
      {clickable && (
        <ArrowUpRight
          size={16}
          className="absolute top-3 right-3 text-slate-600 group-hover:text-brand-400 transition"
        />
      )}
    </Comp>
  );
}

export default function StatCards({ summary }) {
  const navigate = useNavigate();
  if (!summary) return null;
  const top = summary.top_candidate;
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      <Card
        icon="total"
        label="Total Candidates"
        value={summary.total_candidates?.toLocaleString()}
        sub="ranked top 100 of 100,000 pool"
        accent="bg-brand-600/20 text-brand-400"
        onClick={() => navigate("/candidates")}
        hint="View the full ranked candidate list"
      />
      <Card
        icon="avg"
        label="Average Match Score"
        value={summary.avg_match_score}
        sub="across ranked candidates"
        accent="bg-emerald-600/20 text-emerald-400"
        hint="Mean final score across the top 100"
      />
      <Card
        icon="top"
        label="Top Candidate"
        value={top?.candidate_id || "-"}
        sub={top ? `score ${top.score}` : ""}
        accent="bg-amber-600/20 text-amber-400"
        onClick={top ? () => navigate(`/candidates/${top.candidate_id}`) : undefined}
        hint={top ? "Open this candidate's full profile" : undefined}
      />
      <Card
        icon="skills"
        label="Total Skills Matched"
        value={summary.total_skills_matched?.toLocaleString()}
        sub={`${summary.honeypots_in_top100 ?? 0} honeypots in top 100`}
        accent="bg-fuchsia-600/20 text-fuchsia-400"
        hint="Sum of role-relevant skills matched across the shortlist"
      />
    </div>
  );
}
