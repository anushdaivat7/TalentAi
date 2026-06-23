import { useEffect, useRef, useState } from "react";
import { Send, Bot, User } from "lucide-react";
import { sendChat, getChatSuggestions } from "../api";

export default function Chatbot() {
  const [messages, setMessages] = useState([
    {
      role: "bot",
      text: "Hi! I'm your AI recruiting assistant. Ask me about the ranked candidates for the Senior AI Engineer role.",
    },
  ]);
  const [input, setInput] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    getChatSuggestions().then((d) => setSuggestions(d.suggestions || []));
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const ask = async (text) => {
    const q = text ?? input;
    if (!q.trim()) return;
    setMessages((m) => [...m, { role: "user", text: q }]);
    setInput("");
    setLoading(true);
    try {
      const res = await sendChat(q);
      setMessages((m) => [
        ...m,
        { role: "bot", text: res.answer, source: res.source, candidates: res.candidates },
      ]);
    } catch {
      setMessages((m) => [...m, { role: "bot", text: "Sorry, something went wrong." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card flex flex-col h-[70vh]">
      <div className="p-4 border-b border-slate-800 flex items-center gap-2">
        <Bot className="text-brand-400" size={20} />
        <span className="font-semibold">AI Recruiter Chatbot</span>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex gap-3 ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            {m.role === "bot" && (
              <div className="p-2 rounded-lg bg-brand-600/20 h-fit">
                <Bot size={16} className="text-brand-400" />
              </div>
            )}
            <div
              className={`max-w-[75%] rounded-2xl px-4 py-2 text-sm whitespace-pre-wrap ${
                m.role === "user"
                  ? "bg-brand-600 text-white"
                  : "bg-slate-800 text-slate-200"
              }`}
            >
              {m.text}
              {m.source && (
                <div className="text-[10px] opacity-50 mt-1">via {m.source}</div>
              )}
            </div>
            {m.role === "user" && (
              <div className="p-2 rounded-lg bg-slate-700 h-fit">
                <User size={16} />
              </div>
            )}
          </div>
        ))}
        {loading && <div className="text-slate-500 text-sm">Thinking…</div>}
        <div ref={endRef} />
      </div>

      {suggestions.length > 0 && (
        <div className="px-4 pb-2 flex flex-wrap gap-2">
          {suggestions.map((s, i) => (
            <button
              key={i}
              onClick={() => ask(s)}
              className="text-xs px-2 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      <div className="p-4 border-t border-slate-800 flex gap-2">
        <input
          className="input flex-1"
          placeholder="Ask about candidates..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && ask()}
        />
        <button className="btn" onClick={() => ask()} disabled={loading}>
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}
