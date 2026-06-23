export default function ScoreBadge({ score }) {
  let cls = "bg-slate-700 text-slate-200";
  if (score >= 80) cls = "bg-emerald-600/30 text-emerald-300";
  else if (score >= 60) cls = "bg-amber-600/30 text-amber-300";
  else if (score >= 40) cls = "bg-orange-600/30 text-orange-300";
  else cls = "bg-rose-600/30 text-rose-300";
  return <span className={`badge ${cls} font-semibold`}>{score}</span>;
}
