import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell,
} from "recharts";
import { ShieldAlert, ShieldCheck, Bug, Skull } from "lucide-react";

const tooltipStyle = {
  contentStyle: {
    background: "#0f172a",
    border: "1px solid #334155",
    borderRadius: 12,
    color: "#e2e8f0",
  },
};

const LABELS = {
  "entire career at IT-services/consulting firms": "Consulting-only career",
  "non-technical role with no AI/ML career evide": "Non-tech, no AI/ML evidence",
  "non-technical role with no AI/ML career evidence": "Non-tech, no AI/ML evidence",
  "inactive and low recruiter response rate": "Inactive / low response",
  "job-hopper pattern": "Job-hopper pattern",
  "computer-vision/speech/robotics focus without": "CV/Speech/Robotics (off-domain)",
  "keyword stuffer": "Keyword stuffer",
  "research-only background with no production deployment": "Research-only, no prod",
};

function humanize(cat) {
  return LABELS[cat] || cat;
}

function Metric({ icon: Icon, label, value, accent }) {
  return (
    <div className="flex items-center gap-3 rounded-xl bg-slate-900/60 border border-slate-800 p-3">
      <div className={`p-2 rounded-lg ${accent}`}>
        <Icon size={18} />
      </div>
      <div>
        <div className="text-xl font-bold leading-none">{value}</div>
        <div className="text-xs text-slate-400 mt-1">{label}</div>
      </div>
    </div>
  );
}

export default function TrapPanel({ stats, onTrapClick }) {
  if (!stats) return null;
  const cats = (stats.soft_trap_categories || []).map((c) => ({
    ...c,
    label: humanize(c.category),
  }));
  const fmt = (n) => (n === null || n === undefined ? "-" : n.toLocaleString());

  return (
    <div className="card p-5">
      <div className="flex items-center gap-2 mb-1">
        <ShieldAlert className="text-rose-400" size={20} />
        <h3 className="font-semibold text-slate-200">
          Integrity & Trap Detection
        </h3>
      </div>
      <p className="text-xs text-slate-500 mb-4">
        Honeypots are impossible/contradictory profiles planted in the dataset.
        We disqualify them and apply graded penalties to softer red-flag patterns
        so they cannot rank above genuine talent.
      </p>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
        <Metric
          icon={Skull}
          label="Honeypots disqualified (pool)"
          value={fmt(stats.honeypots_detected)}
          accent="bg-rose-600/20 text-rose-300"
        />
        <Metric
          icon={ShieldCheck}
          label={`Honeypots in top ${fmt(stats.top_k)}`}
          value={fmt(stats.honeypots_in_top)}
          accent="bg-emerald-600/20 text-emerald-300"
        />
        <Metric
          icon={Bug}
          label="Soft-trap candidates flagged"
          value={fmt(
            cats.reduce((a, c) => a + (c.count || 0), 0)
          )}
          accent="bg-amber-600/20 text-amber-300"
        />
        <Metric
          icon={ShieldAlert}
          label="Profiles scanned"
          value={fmt(stats.total_scanned)}
          accent="bg-brand-600/20 text-brand-300"
        />
      </div>

      {cats.length > 0 && (
        <>
          <div className="text-xs text-slate-400 mb-2">
            Soft-trap categories (click a bar to filter the table)
          </div>
          <div style={{ width: "100%", height: 240 }}>
            <ResponsiveContainer>
              <BarChart data={cats} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis type="number" stroke="#64748b" fontSize={12} />
                <YAxis
                  type="category"
                  dataKey="label"
                  stroke="#64748b"
                  fontSize={10}
                  width={170}
                />
                <Tooltip {...tooltipStyle} cursor={{ fill: "#1e293b55" }} />
                <Bar
                  dataKey="count"
                  radius={[0, 6, 6, 0]}
                  onClick={(d) => onTrapClick && onTrapClick(d)}
                  className="cursor-pointer"
                >
                  {cats.map((_, i) => (
                    <Cell key={i} fill="#f43f5e" />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  );
}
