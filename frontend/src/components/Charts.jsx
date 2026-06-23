import {
  Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  Legend, ComposedChart, Line, LabelList,
} from "recharts";

// Stable colors for the five scoring components.
const COMPONENT_COLORS = {
  Skill: "#6366f1",
  Experience: "#22c55e",
  Project: "#f59e0b",
  Education: "#ec4899",
  Behavioral: "#06b6d4",
};
const COMPONENTS = ["Skill", "Experience", "Project", "Education", "Behavioral"];

function Panel({ title, subtitle, children, full }) {
  return (
    <div className={`card p-5 ${full ? "lg:col-span-2" : ""}`}>
      <h3 className="font-semibold text-slate-200">{title}</h3>
      {subtitle && <p className="text-xs text-slate-500 mt-0.5 mb-3">{subtitle}</p>}
      <div className={subtitle ? "" : "mt-4"} style={{ width: "100%", height: full ? 320 : 260 }}>
        {children}
      </div>
    </div>
  );
}

const tooltipStyle = {
  contentStyle: {
    background: "#0f172a",
    border: "1px solid #334155",
    borderRadius: 12,
    color: "#e2e8f0",
  },
};

// Tooltip that shows the full score math: base x role-fit x trap = final.
function ScoreTooltip({ active, payload }) {
  if (!active || !payload || !payload.length) return null;
  const d = payload[0]?.payload;
  if (!d) return null;
  const base = COMPONENTS.reduce((a, k) => a + (d[k] || 0), 0);
  const roleFactor = 0.35 + 0.65 * ((d.role_fit ?? 100) / 100); // matches scoring.py
  const trapFactor = (d.trap_penalty ?? 100) / 100;
  const fmt = (n) => Number(n).toFixed(1);
  return (
    <div style={{ ...tooltipStyle.contentStyle, padding: "10px 12px", fontSize: 12 }}>
      <div style={{ fontWeight: 700, marginBottom: 6 }}>
        {d.candidate_id} · rank #{d.rank}
      </div>
      {COMPONENTS.map((k) => (
        <div key={k} style={{ display: "flex", justifyContent: "space-between", gap: 16 }}>
          <span style={{ color: COMPONENT_COLORS[k] }}>{k}</span>
          <span>{fmt(d[k])}</span>
        </div>
      ))}
      <div style={{ borderTop: "1px solid #334155", margin: "6px 0" }} />
      <div style={{ display: "flex", justifyContent: "space-between", gap: 16 }}>
        <span style={{ color: "#94a3b8" }}>Base</span>
        <span>{fmt(base)}</span>
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 16 }}>
        <span style={{ color: "#94a3b8" }}>Role-fit factor</span>
        <span>×{roleFactor.toFixed(2)}</span>
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 16 }}>
        <span style={{ color: "#94a3b8" }}>Trap penalty</span>
        <span>×{trapFactor.toFixed(2)}</span>
      </div>
      <div style={{
        display: "flex", justifyContent: "space-between", gap: 16,
        marginTop: 4, fontWeight: 700, color: "#a5b4fc",
      }}>
        <span>Final score</span>
        <span>{fmt(d.final_score)}</span>
      </div>
    </div>
  );
}

export default function Charts({ charts, onFilter }) {
  if (!charts) return null;

  return (
    <div className="grid grid-cols-1 gap-4">
      {/* Stacked score-breakdown: visually proves the weighted scoring logic */}
      <Panel
        full
        title="How the Top 10 Earn Their Score"
        subtitle="Stacked bars = weighted points per component (Skill 40 · Experience 25 · Project 15 · Education 10 · Behavioral 10) = base score. The white dot/label is the FINAL score after the role-fit & trap multipliers (base × role-fit × trap). Hover any bar for the full math."
      >
        <ResponsiveContainer>
          <ComposedChart data={charts.score_breakdown} margin={{ top: 18 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="candidate_id" stroke="#64748b" fontSize={10}
              angle={-25} textAnchor="end" height={60} interval={0} />
            <YAxis stroke="#64748b" fontSize={12} domain={[0, 100]} />
            <Tooltip content={<ScoreTooltip />} cursor={{ fill: "#1e293b55" }} />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            {COMPONENTS.map((k) => (
              <Bar key={k} dataKey={k} stackId="s" fill={COMPONENT_COLORS[k]}
                radius={k === "Behavioral" ? [4, 4, 0, 0] : [0, 0, 0, 0]} />
            ))}
            <Line
              type="monotone"
              dataKey="final_score"
              name="Final score"
              stroke="#f8fafc"
              strokeWidth={0}
              dot={{ r: 4, fill: "#f8fafc", stroke: "#0f172a", strokeWidth: 1 }}
              activeDot={{ r: 5 }}
              isAnimationActive={false}
            >
              <LabelList
                dataKey="final_score"
                position="top"
                offset={8}
                style={{ fill: "#f1f5f9", fontSize: 10, fontWeight: 700 }}
              />
            </Line>
          </ComposedChart>
        </ResponsiveContainer>
      </Panel>

      <SkillCoverage data={charts.skill_distribution} onFilter={onFilter} />
    </div>
  );
}

function SkillCoverage({ data, onFilter }) {
  const rows = (data || []).slice(0, 8);
  const total = 100; // top-100 shortlist
  return (
    <div className="card p-5">
      <h3 className="font-semibold text-slate-200">Skill Coverage Across the Shortlist</h3>
      <p className="text-xs text-slate-500 mt-0.5 mb-4">
        Share of the Top 100 bringing each role-critical skill — proof the ranking is
        skill-driven.{onFilter ? " Click a skill to filter the table." : ""}
      </p>
      <div className="grid sm:grid-cols-2 gap-x-6 gap-y-2.5">
        {rows.map((r) => {
          const pct = Math.round((r.count / total) * 100);
          const Row = onFilter ? "button" : "div";
          return (
            <Row
              key={r.skill}
              onClick={onFilter ? () => onFilter({ label: `Skill: ${r.skill}`, skill: r.skill }) : undefined}
              className={`text-left w-full group ${onFilter ? "cursor-pointer" : ""}`}
            >
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-slate-300 truncate pr-2 group-hover:text-white">
                  {r.skill}
                </span>
                <span className="text-slate-400 tabular-nums shrink-0">
                  {r.count}/{total} <span className="text-slate-500">({pct}%)</span>
                </span>
              </div>
              <div className="h-1.5 rounded-full bg-slate-800 overflow-hidden">
                <div className="h-full bg-emerald-500 group-hover:bg-emerald-400"
                  style={{ width: `${pct}%` }} />
              </div>
            </Row>
          );
        })}
      </div>
    </div>
  );
}
