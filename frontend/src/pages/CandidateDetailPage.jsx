import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft, CheckCircle2, AlertTriangle, Sparkles,
} from "lucide-react";
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer,
} from "recharts";
import { getCandidate } from "../api";
import ScoreBadge from "../components/ScoreBadge";

export default function CandidateDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    setData(null);
    setError(false);
    getCandidate(id).then(setData).catch(() => setError(true));
  }, [id]);

  const r = data?.ranking;
  const radar = r
    ? [
        { k: "Skill", v: (r.components?.skill_match || 0) * 100 },
        { k: "Experience", v: (r.components?.experience_match || 0) * 100 },
        { k: "Projects", v: (r.components?.project_relevance || 0) * 100 },
        { k: "Education", v: (r.components?.education_match || 0) * 100 },
        { k: "Behavioral", v: (r.components?.behavioral || 0) * 100 },
        { k: "Role fit", v: (r.components?.role_fit || 0) * 100 },
      ]
    : [];

  return (
    <div className="space-y-4">
      <button
        className="btn-ghost text-sm flex items-center gap-1.5"
        onClick={() => (window.history.length > 1 ? navigate(-1) : navigate("/candidates"))}
      >
        <ArrowLeft size={15} /> Back
      </button>

      {error ? (
        <div className="card p-8 text-center text-slate-400">
          Candidate <code className="text-slate-200">{id}</code> not found in the ranking.
        </div>
      ) : !r ? (
        <div className="card p-12 text-center text-slate-400">Loading...</div>
      ) : (
        <>
          <div className="card p-6">
            <div className="flex items-center gap-3 flex-wrap">
              <h2 className="text-xl font-bold">{r.candidate_id}</h2>
              <ScoreBadge score={r.final_score} />
              <span className="badge bg-slate-700 text-slate-300">rank #{r.rank}</span>
              {r.is_honeypot && (
                <span className="badge bg-rose-600/30 text-rose-300">honeypot</span>
              )}
            </div>
            <div className="text-slate-400 mt-1">
              {r.current_title} @ {r.current_company} · {r.location}, {r.country} ·{" "}
              {r.years_experience} yrs
            </div>
          </div>

          <div className="card p-4 bg-brand-600/10 border-brand-700/40">
            <div className="flex items-center gap-2 text-brand-300 font-medium mb-1">
              <Sparkles size={16} /> AI Explanation
            </div>
            <p className="text-slate-200 text-sm">{r.explanation}</p>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div className="card p-4">
              <div className="flex items-center gap-2 text-emerald-400 font-medium mb-2">
                <CheckCircle2 size={16} /> Strengths
              </div>
              <ul className="space-y-1 text-sm text-slate-300 list-disc list-inside">
                {r.strengths?.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
            <div className="card p-4">
              <div className="flex items-center gap-2 text-amber-400 font-medium mb-2">
                <AlertTriangle size={16} /> Weaknesses / Concerns
              </div>
              <ul className="space-y-1 text-sm text-slate-300 list-disc list-inside">
                {r.weaknesses?.length ? (
                  r.weaknesses.map((s, i) => <li key={i}>{s}</li>)
                ) : (
                  <li className="text-slate-500">No major concerns</li>
                )}
              </ul>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div className="card p-4">
              <div className="font-medium mb-2 text-slate-200">Score breakdown</div>
              <div style={{ width: "100%", height: 260 }}>
                <ResponsiveContainer>
                  <RadarChart data={radar}>
                    <PolarGrid stroke="#334155" />
                    <PolarAngleAxis dataKey="k" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                    <Radar dataKey="v" stroke="#6366f1" fill="#6366f1" fillOpacity={0.5} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="card p-4">
              <div className="font-medium mb-2 text-slate-200">Matching skills</div>
              <div className="flex flex-wrap gap-2 mb-3">
                {r.matching_skills?.map((s, i) => (
                  <span key={i} className="badge bg-emerald-600/20 text-emerald-300">
                    {s}
                  </span>
                ))}
              </div>
              <div className="font-medium mb-2 text-slate-200">Missing skills</div>
              <div className="flex flex-wrap gap-2">
                {r.missing_skills?.length ? (
                  r.missing_skills.map((s, i) => (
                    <span key={i} className="badge bg-rose-600/20 text-rose-300">
                      {s}
                    </span>
                  ))
                ) : (
                  <span className="text-slate-500 text-sm">none</span>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
