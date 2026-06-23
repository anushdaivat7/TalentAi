import { useEffect, useState } from "react";
import { Search, SlidersHorizontal, ShieldAlert, X } from "lucide-react";
import { searchCandidates } from "../api";
import ScoreBadge from "./ScoreBadge";

const SORTS = [
  { v: "rank", l: "Rank" },
  { v: "score", l: "Score" },
  { v: "experience", l: "Experience" },
];

export default function CandidateTable({ onSelect, extFilter, onClearFilter }) {
  const [q, setQ] = useState("");
  const [skill, setSkill] = useState("");
  const [minExp, setMinExp] = useState("");
  const [minScore, setMinScore] = useState("");
  const [sort, setSort] = useState("rank");
  const [hideHoney, setHideHoney] = useState(false);
  const [data, setData] = useState({ results: [], total: 0 });
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const params = { sort, limit: 100, hide_honeypots: hideHoney };
      if (q) params.q = q;
      if (skill) params.skill = skill;
      if (minExp) params.min_experience = minExp;
      if (minScore) params.min_score = minScore;
      // External filters from clickable charts (override/augment manual ones).
      if (extFilter) {
        if (extFilter.skill) params.skill = extFilter.skill;
        if (extFilter.min_score !== undefined) params.min_score = extFilter.min_score;
        if (extFilter.max_score !== undefined) params.max_score = extFilter.max_score;
        if (extFilter.min_experience !== undefined)
          params.min_experience = extFilter.min_experience;
        if (extFilter.max_experience !== undefined)
          params.max_experience = extFilter.max_experience;
        if (extFilter.trap) params.trap = extFilter.trap;
      }
      const res = await searchCandidates(params);
      setData(res);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const t = setTimeout(fetchData, 250);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q, skill, minExp, minScore, sort, hideHoney, extFilter]);

  return (
    <div className="card p-5">
      <div className="flex flex-wrap items-center gap-3 mb-4">
        <div className="relative flex-1 min-w-[220px]">
          <Search size={16} className="absolute left-3 top-3 text-slate-500" />
          <input
            className="input w-full pl-9"
            placeholder="Search by candidate, title, location..."
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </div>
        <input
          className="input w-36"
          placeholder="Skill"
          value={skill}
          onChange={(e) => setSkill(e.target.value)}
        />
        <input
          className="input w-28"
          type="number"
          placeholder="Min exp"
          value={minExp}
          onChange={(e) => setMinExp(e.target.value)}
        />
        <input
          className="input w-28"
          type="number"
          placeholder="Min score"
          value={minScore}
          onChange={(e) => setMinScore(e.target.value)}
        />
        <select className="input" value={sort} onChange={(e) => setSort(e.target.value)}>
          {SORTS.map((s) => (
            <option key={s.v} value={s.v}>
              Sort: {s.l}
            </option>
          ))}
        </select>
        <button
          className={`btn-ghost ${hideHoney ? "ring-2 ring-rose-500" : ""}`}
          onClick={() => setHideHoney((v) => !v)}
          title="Hide honeypot / impossible profiles"
        >
          <ShieldAlert size={16} /> {hideHoney ? "Honeypots hidden" : "Hide honeypots"}
        </button>
      </div>

      {extFilter && (
        <div className="mb-3 flex items-center gap-2">
          <span className="badge bg-brand-600/30 text-brand-200 flex items-center gap-1.5">
            Filtered by chart: {extFilter.label}
            <button
              onClick={onClearFilter}
              className="hover:text-white"
              title="Clear chart filter"
            >
              <X size={13} />
            </button>
          </span>
        </div>
      )}

      <div className="text-xs text-slate-500 mb-2 flex items-center gap-2">
        <SlidersHorizontal size={14} /> {loading ? "Loading..." : `${data.total} match(es)`}
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-400 border-b border-slate-800">
              <th className="py-2 pr-3">#</th>
              <th className="py-2 pr-3">Candidate</th>
              <th className="py-2 pr-3">Title</th>
              <th className="py-2 pr-3">Exp</th>
              <th className="py-2 pr-3">Location</th>
              <th className="py-2 pr-3">Score</th>
              <th className="py-2 pr-3">Top skills</th>
            </tr>
          </thead>
          <tbody>
            {data.results.map((r) => (
              <tr
                key={r.candidate_id}
                onClick={() => onSelect(r.candidate_id)}
                className="border-b border-slate-800/60 hover:bg-slate-800/40 cursor-pointer"
              >
                <td className="py-2 pr-3 text-slate-400">{r.rank}</td>
                <td className="py-2 pr-3 font-medium">
                  {r.candidate_id}
                  {r.is_honeypot && (
                    <span className="badge bg-rose-600/30 text-rose-300 ml-2">honeypot</span>
                  )}
                </td>
                <td className="py-2 pr-3 text-slate-300">{r.current_title}</td>
                <td className="py-2 pr-3 text-slate-300">{r.years_experience}y</td>
                <td className="py-2 pr-3 text-slate-400">{r.location}</td>
                <td className="py-2 pr-3">
                  <ScoreBadge score={r.final_score} />
                </td>
                <td className="py-2 pr-3 text-slate-400 max-w-[260px] truncate">
                  {(r.matching_skills || []).slice(0, 3).join(", ")}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
