import { useState } from "react";
import { Download, FileCheck2, RefreshCw, CheckCircle2, XCircle, FileText } from "lucide-react";
import {
  generateSubmission, validateSubmission, downloadSubmissionUrl, downloadReportPdfUrl,
} from "../api";

export default function SubmissionPanel() {
  const [team, setTeam] = useState("team_talentai");
  const [status, setStatus] = useState(null);
  const [validation, setValidation] = useState(null);
  const [busy, setBusy] = useState(false);

  const run = async () => {
    setBusy(true);
    setValidation(null);
    try {
      const gen = await generateSubmission(team);
      setStatus(gen);
      const val = await validateSubmission(team);
      setValidation(val);
    } catch (e) {
      setStatus({ error: e?.response?.data?.detail || "failed" });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="card p-6 max-w-2xl">
      <h2 className="text-xl font-bold mb-1">Submission Generator</h2>
      <p className="text-slate-400 text-sm mb-4">
        Produces a spec-compliant CSV (<code>candidate_id,rank,score,reasoning</code>),
        exactly 100 rows, validated with the official <code>validate_submission.py</code>.
      </p>

      <div className="flex gap-2 mb-4">
        <input
          className="input flex-1"
          value={team}
          onChange={(e) => setTeam(e.target.value)}
          placeholder="participant / team id"
        />
        <button className="btn" onClick={run} disabled={busy}>
          {busy ? <RefreshCw size={16} className="animate-spin" /> : <FileCheck2 size={16} />}
          Generate & Validate
        </button>
      </div>

      {status?.error && <div className="text-rose-400 text-sm">{status.error}</div>}

      {status && !status.error && (
        <div className="card p-4 mb-3 text-sm">
          <div className="text-slate-300">
            Wrote <span className="font-mono">{status.rows}</span> rows for team{" "}
            <span className="font-semibold">{status.team}</span>.
          </div>
          <div className="text-slate-500 text-xs break-all mt-1">{status.path}</div>
        </div>
      )}

      {validation && (
        <div
          className={`card p-4 mb-3 ${
            validation.valid ? "border-emerald-700/50" : "border-rose-700/50"
          }`}
        >
          {validation.valid ? (
            <div className="flex items-center gap-2 text-emerald-400 font-medium">
              <CheckCircle2 size={18} /> Submission is valid
            </div>
          ) : (
            <div className="text-rose-400">
              <div className="flex items-center gap-2 font-medium mb-2">
                <XCircle size={18} /> Validation failed
              </div>
              <ul className="text-xs list-disc list-inside space-y-1">
                {validation.errors?.map((e, i) => (
                  <li key={i}>{e}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <div className="flex flex-wrap gap-2">
        {validation?.valid && (
          <a className="btn" href={downloadSubmissionUrl(team)} download>
            <Download size={16} /> Download {team}.csv
          </a>
        )}
        <a
          className="btn-ghost"
          href={downloadReportPdfUrl(team)}
          target="_blank"
          rel="noreferrer"
        >
          <FileText size={16} /> Download PDF report
        </a>
      </div>
      <p className="text-xs text-slate-500 mt-2">
        The PDF contains a formatted summary plus a full ranked-candidates table
        (rank, ID, score, title, experience, education, location, reasoning).
      </p>
    </div>
  );
}
