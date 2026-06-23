import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { getSummary, getCharts, getTrapStats, searchCandidates } from "../api";
import { filterToParams } from "../lib/filters";
import StatCards from "../components/StatCards";
import PipelinePanel from "../components/PipelinePanel";
import Charts from "../components/Charts";
import TrapPanel from "../components/TrapPanel";
import ScoreBadge from "../components/ScoreBadge";

export default function OverviewPage() {
  const [summary, setSummary] = useState(null);
  const [charts, setCharts] = useState(null);
  const [trapStats, setTrapStats] = useState(null);
  const [top10, setTop10] = useState([]);
  const navigate = useNavigate();
  const trapRef = useRef(null);
  const top10Ref = useRef(null);

  const showTrap = () =>
    trapRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  const showTop10 = () =>
    top10Ref.current?.scrollIntoView({ behavior: "smooth", block: "start" });

  useEffect(() => {
    getSummary().then(setSummary).catch(() => {});
    getCharts().then(setCharts).catch(() => {});
    getTrapStats().then(setTrapStats).catch(() => {});
    searchCandidates({ sort: "rank", limit: 10 })
      .then((d) => setTop10(d.results || []))
      .catch(() => {});
  }, []);

  const goFilter = (filter) =>
    navigate(`/candidates?${filterToParams(filter).toString()}`);

  return (
    <div className="space-y-6">
      <StatCards summary={summary} />
      <PipelinePanel stats={trapStats} onShowTrap={showTrap} onShowTop10={showTop10} />
      <Charts charts={charts} onFilter={goFilter} />
      <div ref={trapRef} className="scroll-mt-20">
        <TrapPanel
          stats={trapStats}
          onTrapClick={(d) =>
            goFilter({ label: `Trap: ${d.label}`, trap: d.category })
          }
        />
      </div>

      <div ref={top10Ref} className="card p-5 scroll-mt-20">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="font-semibold text-slate-200">Top 10 Candidates</h3>
            <p className="text-xs text-slate-500">The highest-ranked matches for this role</p>
          </div>
          <Link
            to="/candidates"
            className="btn-ghost text-sm flex items-center gap-1.5"
          >
            View all candidates <ArrowRight size={15} />
          </Link>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-400 border-b border-slate-800">
                <th className="py-2 pr-3">#</th>
                <th className="py-2 pr-3">Candidate</th>
                <th className="py-2 pr-3">Title</th>
                <th className="py-2 pr-3">Exp</th>
                <th className="py-2 pr-3">Score</th>
              </tr>
            </thead>
            <tbody>
              {top10.map((r) => (
                <tr
                  key={r.candidate_id}
                  onClick={() => navigate(`/candidates/${r.candidate_id}`)}
                  className="border-b border-slate-800/60 hover:bg-slate-800/40 cursor-pointer"
                >
                  <td className="py-2 pr-3 text-slate-400">{r.rank}</td>
                  <td className="py-2 pr-3 font-medium">{r.candidate_id}</td>
                  <td className="py-2 pr-3 text-slate-300">{r.current_title}</td>
                  <td className="py-2 pr-3 text-slate-300">{r.years_experience}y</td>
                  <td className="py-2 pr-3">
                    <ScoreBadge score={r.final_score} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
