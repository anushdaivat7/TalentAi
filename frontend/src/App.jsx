import { Suspense, lazy, useEffect, useState } from "react";
import { NavLink, Navigate, Route, Routes } from "react-router-dom";
import {
  LayoutDashboard, Users, Briefcase, Bot, FileCheck2, BrainCircuit, AlertCircle,
} from "lucide-react";
import { getHealth } from "./api";

const OverviewPage = lazy(() => import("./pages/OverviewPage"));
const CandidatesPage = lazy(() => import("./pages/CandidatesPage"));
const CandidateDetailPage = lazy(() => import("./pages/CandidateDetailPage"));
const JobProfilePage = lazy(() => import("./pages/JobProfilePage"));
const ChatPage = lazy(() => import("./pages/ChatPage"));
const SubmissionPage = lazy(() => import("./pages/SubmissionPage"));

const TABS = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/candidates", label: "Candidates", icon: Users },
  { to: "/job", label: "Job Profile", icon: Briefcase },
  { to: "/chat", label: "AI Chatbot", icon: Bot },
  { to: "/submission", label: "Submission", icon: FileCheck2 },
];

function Loader() {
  return <div className="card p-12 text-center text-slate-400">Loading...</div>;
}

export default function App() {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    getHealth().then(setHealth).catch(() => setHealth({ status: "down" }));
  }, []);

  const noData = health && (health.status === "down" || health.ranked_count === 0);

  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-800 sticky top-0 z-40 bg-slate-950/80 backdrop-blur">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <NavLink to="/" className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-brand-600/20">
              <BrainCircuit className="text-brand-400" size={24} />
            </div>
            <div>
              <h1 className="font-bold text-lg leading-tight">TalentAI</h1>
              <p className="text-xs text-slate-500">
                Intelligent Candidate Discovery &amp; Ranking
              </p>
            </div>
          </NavLink>
          <nav className="hidden md:flex gap-1">
            {TABS.map((t) => {
              const Icon = t.icon;
              return (
                <NavLink
                  key={t.to}
                  to={t.to}
                  end={t.end}
                  className={({ isActive }) =>
                    `flex items-center gap-2 px-3 py-2 rounded-xl text-sm transition ${
                      isActive
                        ? "bg-brand-600 text-white"
                        : "text-slate-400 hover:bg-slate-800"
                    }`
                  }
                >
                  <Icon size={16} /> {t.label}
                </NavLink>
              );
            })}
          </nav>
        </div>
        <nav className="md:hidden flex gap-1 px-2 pb-2 overflow-x-auto">
          {TABS.map((t) => (
            <NavLink
              key={t.to}
              to={t.to}
              end={t.end}
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-lg text-xs whitespace-nowrap ${
                  isActive ? "bg-brand-600 text-white" : "text-slate-400 bg-slate-800"
                }`
              }
            >
              {t.label}
            </NavLink>
          ))}
        </nav>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        {noData && (
          <div className="card p-4 border-amber-700/50 flex items-center gap-3 text-amber-300">
            <AlertCircle size={18} />
            <span className="text-sm">
              No ranking loaded. Run{" "}
              <code className="text-amber-200">python ranking-engine/run_ranking.py</code> then{" "}
              <code className="text-amber-200">POST /api/reload</code>.
            </span>
          </div>
        )}

        <Suspense fallback={<Loader />}>
          <Routes>
            <Route path="/" element={<OverviewPage />} />
            <Route path="/candidates" element={<CandidatesPage />} />
            <Route path="/candidates/:id" element={<CandidateDetailPage />} />
            <Route path="/job" element={<JobProfilePage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/submission" element={<SubmissionPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </main>

      <footer className="max-w-7xl mx-auto px-4 py-6 text-center text-xs text-slate-600">
        TalentAI · Redrob India Runs Data &amp; AI Challenge · MiniLM embeddings + FAISS +
        rule-based ranking + Gemini explanations
      </footer>
    </div>
  );
}
