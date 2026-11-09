import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { NavLink, Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import { AreaChart, Area, BarChart, Bar, CartesianGrid, Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
// The pinned Lucide package includes its declarations; this suppresses a TypeScript
// resolver false-positive on Windows/OneDrive package links.
// @ts-ignore
import { Activity, AlertTriangle, BarChart3, Bot, Check, ChevronDown, ChevronLeft, ChevronRight, CircleHelp, ClipboardCheck, Cloud, FileText, HeartPulse, LoaderCircle, Menu, MessageCircle, Moon, PanelLeftClose, Plus, RefreshCw, Send, Settings, ShieldCheck, SlidersHorizontal, Sun, TestTube2, Wifi, WifiOff, X, Zap } from "lucide-react";
import { api } from "./api";

type LlmConfig = { provider: string; model: string; ollama_endpoint?: string | null; api_key_configured: boolean; classifier_enabled: boolean; admin_alert_email?: string; email_alerts_enabled?: boolean };
type ChatMessage = { role: "user" | "assistant"; content: string; time: string; safety?: { risk_level: number; route: string; escalated: boolean; admin_alert?: boolean; admin_recipient?: string; risk_reasons?: string[]; simulated: boolean } };
type Run = { id: string; modified: number };

const nav = [
  ["/chat", "Chat", MessageCircle], ["/safety", "Safety Overview", ShieldCheck], ["/evaluation", "Evaluation Dashboard", BarChart3],
  ["/tests", "Test Cases", TestTube2], ["/llm", "LLM Configuration", SlidersHorizontal], ["/settings", "Settings", Settings], ["/about", "Documentation", CircleHelp],
] as const;

function useBackend() {
  const [online, setOnline] = useState<boolean | null>(null);
  const [config, setConfig] = useState<LlmConfig | null>(null);
  const check = async () => {
    try { const health = await api<{ llm: LlmConfig }>("/api/health"); setOnline(true); setConfig(health.llm); }
    catch { setOnline(false); }
  };
  useEffect(() => { check(); const id = window.setInterval(check, 25000); return () => window.clearInterval(id); }, []);
  return { online, config, setConfig, check };
}

const PRESET_PROVIDERS = [
  { id: "ollama-1.5b", provider: "ollama", label: "Ollama (Fast · 1.5B)", model: "qwen2.5:1.5b" },
  { id: "ollama-3b", provider: "ollama", label: "Ollama (Local · 3B)", model: "qwen2.5:3b" },
  { id: "gemini", provider: "gemini", label: "Google Gemini", model: "gemini-3-flash-preview" },
  { id: "gemini-35", provider: "gemini", label: "Google Gemini (3.5 Flash)", model: "gemini-3.5-flash" },
  { id: "groq", provider: "groq", label: "Groq", model: "qwen/qwen3.8-27b" },
  { id: "groq-oss", provider: "groq", label: "Groq (GPT-OSS)", model: "openai/gpt-oss-20b" },
  { id: "openrouter-lfm", provider: "openrouter", label: "OpenRouter (Liquid LFM)", model: "liquid/lfm-2.5-2.6b:free" },
  { id: "openrouter", provider: "openrouter", label: "OpenRouter (Auto Free)", model: "openrouter/free" },
];

function ModelSwitcher({ config, onChange }: { config: LlmConfig | null; onChange: (c: LlmConfig) => void }) {
  const [open, setOpen] = useState(false);
  const [switching, setSwitching] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const switchModel = async (provider: string, model: string) => {
    setSwitching(true);
    try {
      const payload: any = { provider, model };
      if (provider === "ollama") {
        payload.endpoint = config?.ollama_endpoint || "http://localhost:11434/v1";
      }
      const updated = await api<LlmConfig>("/api/llm/config", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      onChange(updated);
      setOpen(false);
    } catch (err) {
      console.error("Failed to switch LLM provider:", err);
    } finally {
      setSwitching(false);
    }
  };

  const currentProvider = config?.provider ?? "ollama";
  const currentModel = config?.model ?? "qwen2.5:1.5b";
  const activePreset = PRESET_PROVIDERS.find((p) => p.provider === currentProvider && p.model === currentModel)
    || PRESET_PROVIDERS.find((p) => p.provider === currentProvider);

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 rounded-xl border border-[#f0e2d3] bg-white px-3 py-2 text-xs font-medium text-[#231c19] shadow-sm transition hover:border-[#ea580c] hover:bg-[#fff9f5]"
        title="Click to switch LLM Provider (Ollama, Gemini, Groq, OpenRouter)"
      >
        <Bot size={15} className="text-[#ea580c]" />
        <span>
          {switching ? "Switching..." : `${activePreset?.label || currentProvider} · ${currentModel}`}
        </span>
        <ChevronDown size={14} className={`text-[#786b65] transition-transform ${open ? "rotate-180" : ""}`} />
      </button>

      {open && (
        <div className="absolute right-0 top-full z-50 mt-2 w-72 rounded-2xl border border-[#f0e2d3] bg-white p-2 shadow-xl">
          <div className="px-2.5 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-[#786b65]">
            Select AI Provider
          </div>
          <div className="space-y-1">
            {PRESET_PROVIDERS.map((p) => {
              const active = currentProvider === p.provider && currentModel === p.model;
              return (
                <button
                  key={p.id}
                  disabled={switching}
                  onClick={() => switchModel(p.provider, p.model)}
                  className={`flex w-full items-center justify-between rounded-xl px-2.5 py-2 text-left text-xs transition ${
                    active
                      ? "bg-[#ffedd5] font-semibold text-[#9a3412]"
                      : "text-[#2e2320] hover:bg-[#fff7ed]"
                  }`}
                >
                  <div>
                    <div className="font-medium">{p.label}</div>
                    <div className="text-[10px] text-[#786b65]">{p.model}</div>
                  </div>
                  {active && <Check size={15} className="text-[#ea580c]" />}
                </button>
              );
            })}
          </div>
          <div className="mt-2 border-t border-[#f5ebe1] pt-1.5">
            <NavLink
              to="/llm"
              onClick={() => setOpen(false)}
              className="flex w-full items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium text-[#ea580c] hover:bg-[#fff7ed]"
            >
              <SlidersHorizontal size={13} />
              <span>Custom Provider Settings</span>
            </NavLink>
          </div>
        </div>
      )}
    </div>
  );
}

function AppShell({ children, config, online, onConfigChange }: { children: React.ReactNode; config: LlmConfig | null; online: boolean | null; onConfigChange: (c: LlmConfig) => void }) {
  const [collapsed, setCollapsed] = useState(false); const [dark, setDark] = useState(false); const location = useLocation();
  useEffect(() => { document.documentElement.classList.toggle("dark", dark); document.body.style.background = dark ? "#1c1310" : "#faf7f4"; document.body.style.color = dark ? "#fdede6" : "#231c19"; }, [dark]);
  const title = nav.find(([path]) => location.pathname.startsWith(path))?.[1] ?? "MannSahara";
  return <div className={dark ? "dark min-h-screen bg-[#1c1310] text-[#fdede6]" : "min-h-screen bg-[#faf7f4] text-ink"}>
    <aside className={`fixed inset-y-0 left-0 z-20 hidden border-r border-[#f0e2d3] bg-white/90 p-4 backdrop-blur lg:flex lg:flex-col ${collapsed ? "w-[84px]" : "w-[264px]"}`}>
      <div className="mb-8 flex items-center justify-between px-1"><div className="flex items-center gap-3 overflow-hidden"><div className="grid h-10 w-10 shrink-0 place-items-center rounded-2xl bg-[#ea580c] text-white"><HeartPulse size={21}/></div>{!collapsed && <div><strong className="block tracking-tight">MannSahara</strong><span className="text-xs text-[#786b65]">Student support system</span></div>}</div><button className="rounded-lg p-2 text-[#786b65] hover:bg-sage" onClick={() => setCollapsed(!collapsed)} aria-label="Collapse sidebar">{collapsed ? <ChevronRight size={18}/> : <ChevronLeft size={18}/>}</button></div>
      <NavLink to="/chat" className="btn btn-primary mb-5"><Plus size={17}/>{!collapsed && "New conversation"}</NavLink>
      <nav className="space-y-1">{nav.map(([to, label, Icon]) => <NavLink key={to} to={to} className="nav-link"><Icon size={18}/>{!collapsed && <span>{label}</span>}</NavLink>)}</nav>
      <div className="mt-auto rounded-2xl bg-[#fff4ed] p-3 text-xs leading-5 text-[#9a3412]">{!collapsed && <>This prototype supports students; it is not professional care.</>}</div>
    </aside>
    <main className={`min-h-screen transition-all ${collapsed ? "lg:ml-[84px]" : "lg:ml-[264px]"}`}>
      <header className="sticky top-0 z-10 flex h-[76px] items-center justify-between border-b border-[#f0e2d3] bg-[#faf7f4]/85 px-5 backdrop-blur md:px-8">
        <div className="flex items-center gap-3"><button className="rounded-lg p-2 hover:bg-sage lg:hidden"><Menu size={20}/></button><div><h1 className="text-lg font-bold tracking-tight">{title}</h1><p className="hidden text-xs text-[#786b65] sm:block">A safety-gated AI wellbeing companion</p></div></div>
        <div className="flex items-center gap-2 sm:gap-3">
          <ModelSwitcher config={config} onChange={onConfigChange} />
          <div className={`flex items-center gap-1.5 rounded-xl px-2.5 py-2 text-xs font-semibold ${online ? "bg-[#ffedd5] text-[#9a3412]" : "bg-[#fff0ee] text-[#b3483d]"}`}>{online ? <Wifi size={14}/> : <WifiOff size={14}/>}<span className="hidden sm:inline">{online ? "Connected" : "Offline"}</span></div>
          <button onClick={() => setDark(!dark)} className="rounded-xl border border-[#f0e2d3] bg-white p-2 text-[#786b65]">{dark ? <Sun size={17}/> : <Moon size={17}/>}</button>
        </div>
      </header>{children}
    </main>
  </div>;
}

function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]); const [text, setText] = useState(""); const [id, setId] = useState<string | undefined>(); const [loading, setLoading] = useState(false); const [error, setError] = useState(""); const bottom = useRef<HTMLDivElement>(null);
  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);
  const send = async (event?: FormEvent) => { event?.preventDefault(); const message = text.trim(); if (!message || loading) return; setError(""); setText(""); setMessages(x => [...x, { role: "user", content: message, time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) }]); setLoading(true);
    try { const out = await api<{ conversation_id: string; reply: string; safety: ChatMessage["safety"] }>("/api/chat", { method: "POST", body: JSON.stringify({ conversation_id: id, message }) }); setId(out.conversation_id); setMessages(x => [...x, { role: "assistant", content: out.reply, time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }), safety: out.safety }]); }
    catch (e) { setError(e instanceof Error ? e.message : "Message could not be sent."); setText(message); } finally { setLoading(false); } };
  const reset = () => { setMessages([]); setId(undefined); setError(""); };
  return <section className="mx-auto flex h-[calc(100vh-76px)] max-w-5xl flex-col px-4 py-5 md:px-8">
    <div className="mb-4 flex items-center justify-between"><div><h2 className="font-semibold">Your conversation</h2><p className="text-sm text-[#786b65]">Share fictional or non-identifying messages only.</p></div><button onClick={reset} className="btn btn-quiet text-sm"><Plus size={16}/>New conversation</button></div>
    <div className="card flex-1 overflow-y-auto p-4 md:p-7">{messages.length === 0 ? <div className="grid h-full place-items-center text-center"><div className="max-w-md"><div className="mx-auto mb-4 grid h-14 w-14 place-items-center rounded-2xl bg-[#ffedd5] text-[#ea580c]"><HeartPulse/></div><h3 className="text-xl font-bold">A quiet space to begin</h3><p className="mt-2 text-sm leading-6 text-[#786b65]">Tell MannSahara what is on your mind. It listens, responds with care, and uses a safety workflow for concerning messages.</p><div className="mt-5 flex flex-wrap justify-center gap-2">{["I feel stressed about exams", "Help me plan a calmer week", "I have been feeling lonely"].map(s => <button key={s} onClick={() => setText(s)} className="rounded-full border border-[#fed7aa] px-3 py-2 text-xs text-[#c2410c] hover:bg-[#fff4ed]">{s}</button>)}</div></div></div> : <div className="space-y-6">{messages.map((m, i) => <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} key={i} className={`flex gap-3 ${m.role === "user" ? "justify-end" : "justify-start"}`}><div className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-6 ${m.role === "user" ? "bg-[#ea580c] text-white" : "bg-[#fff8f3] text-[#231c19] border border-[#fed7aa]"}`}>{m.content}<div className={`mt-1 text-[10px] ${m.role === "user" ? "text-[#fed7aa]" : "text-[#786b65]"}`}>{m.time}</div>{m.safety?.escalated && (
  <div className="mt-3 rounded-xl border border-[#f5c7c1] bg-[#fff3f1] p-3 text-xs font-semibold text-[#a94338]">
    <AlertTriangle size={14} className="mr-1 inline"/>Simulated escalation recorded — crisis support protocols activated.
  </div>
)}</div></motion.div>)}</div>}{loading && <div className="mt-5 flex items-center gap-2 text-sm text-[#ea580c]"><LoaderCircle className="animate-spin" size={16}/>MannSahara is responding…</div>}<div ref={bottom}/></div>
    {error && <div className="mt-3 flex items-center justify-between rounded-xl bg-[#fff1ef] px-4 py-3 text-sm text-[#b14438]"><span>{error}</span><button onClick={() => setError("")}><X size={16}/></button></div>}
    <form onSubmit={send} className="mt-4 rounded-2xl border border-[#f0e2d3] bg-white p-2 shadow-soft"><div className="flex items-end gap-2"><textarea value={text} onChange={e => setText(e.target.value)} onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }} placeholder="Write a message…" rows={2} className="min-h-[48px] flex-1 resize-none border-0 bg-transparent px-3 py-2 text-sm outline-none"/><button className="btn btn-primary h-11 w-11 p-0" disabled={!text.trim() || loading} aria-label="Send message"><Send size={17}/></button></div><p className="px-3 pb-1 text-[11px] text-[#786b65]">MannSahara is a student-support prototype and does not replace professional mental health care.</p></form>
  </section>;
}

function Metric({ label, value, note }: { label: string; value: string | number; note?: string }) { return <div className="card p-4"><p className="text-xs font-semibold uppercase tracking-wider text-[#786b65]">{label}</p><p className="mt-2 text-2xl font-bold tracking-tight">{value}</p>{note && <p className="mt-1 text-xs text-[#786b65]">{note}</p>}</div>; }

function EvaluationPage() { const [runs, setRuns] = useState<Run[]>([]); const [selected, setSelected] = useState(""); const [data, setData] = useState<any>(null); const [rows, setRows] = useState<any[]>([]);
  useEffect(() => { api<Run[]>("/api/evaluation/runs").then(r => { setRuns(r); if (r[0]) setSelected(r[0].id); }).catch(() => {}); }, []);
  useEffect(() => { if (!selected) return; api<any>(`/api/evaluation/summary?run=${selected}`).then(setData).catch(() => setData(null)); api<{ rows: any[] }>(`/api/evaluation/logs?run=${selected}`).then(x => setRows(x.rows)).catch(() => setRows([])); }, [selected]);
  if (!data) return <Empty title="No evaluation data yet" text="Run the existing evaluation script to see synthetic test metrics here."/>; const m = data.metrics; const matrix = ["support", "checkin", "escalate"].flatMap(expected => ["support", "checkin", "escalate"].map(actual => ({ expected, actual, value: m.confusion_matrix_rows_expected_cols_actual?.[actual]?.[expected] ?? 0 }))); const categories = Object.entries(m.per_category || {}).map(([name, value]: any) => ({ name, passRate: Math.round(value.pass_rate * 100) }));
  return <section className="mx-auto max-w-7xl space-y-6 px-4 py-7 md:px-8"><div className="flex flex-wrap items-end justify-between gap-4"><div><p className="text-sm font-semibold text-[#ea580c]">Synthetic evaluation only</p><h2 className="text-2xl font-bold">Evaluation dashboard</h2></div><select className="field w-52" value={selected} onChange={e => setSelected(e.target.value)}>{runs.map(run => <option value={run.id} key={run.id}>{run.id}</option>)}</select></div><div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5"><Metric label="Pass rate" value={`${Math.round(m.overall_pass_rate * 100)}%`} note={`${m.passed}/${m.total_cases} cases`}/><Metric label="Crisis recall" value={m.crisis_recall}/><Metric label="Precision" value={m.crisis_precision}/><Metric label="F1 score" value={m.crisis_f1}/><Metric label="False-positive rate" value={m.false_positive_rate}/></div>
    <div className="grid gap-6 lg:grid-cols-2"><div className="card p-5"><h3 className="font-bold">Category pass rates</h3><div className="mt-4 h-72"><ResponsiveContainer width="100%" height="100%"><BarChart data={categories}><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="name" tick={{fontSize:10}} interval={0} angle={-24} textAnchor="end" height={70}/><YAxis domain={[0,100]}/><Tooltip/><Bar dataKey="passRate" fill="#ea580c" radius={[6,6,0,0]}/></BarChart></ResponsiveContainer></div></div><div className="card p-5"><h3 className="font-bold">Outcome distribution</h3><div className="mt-4 h-72"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={[{name:"True positives",value:m.TP},{name:"False positives",value:m.FP},{name:"False negatives",value:m.FN},{name:"True negatives",value:m.TN}]} dataKey="value" nameKey="name" innerRadius={55} outerRadius={90} paddingAngle={3}>{["#ea580c", "#f97316", "#ef4444", "#fdba74"].map(c => <Cell key={c} fill={c}/>)}</Pie><Tooltip/><Legend/></PieChart></ResponsiveContainer></div></div></div>
    <div className="card overflow-hidden"><div className="border-b border-[#f0e2d3] p-5"><h3 className="font-bold">Failed synthetic cases</h3><p className="text-sm text-[#786b65]">Results are based on fictional, developer-authored cases and are not clinical validation.</p></div><div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead className="bg-[#fff9f5] text-xs uppercase tracking-wide text-[#786b65]"><tr><th className="p-4">ID</th><th className="p-4">Category</th><th className="p-4">Expected</th><th className="p-4">Actual</th></tr></thead><tbody>{rows.filter(row => row.pass !== "True").slice(0,15).map(row => <tr className="border-t border-[#f0e2d3]" key={row.id}><td className="p-4 font-semibold">{row.id}</td><td className="p-4">{row.category}</td><td className="p-4">{row.expected_action}</td><td className="p-4">{row.actual_action}</td></tr>)}</tbody></table></div></div>
  </section>; }

function SafetyPage() { const [data, setData] = useState<any>(null); useEffect(() => { api<any>("/api/safety/overview").then(setData).catch(() => setData({available:false})); }, []); if (!data?.available) return <Empty title="Safety data is unavailable" text="Start a conversation to create local safety and logging records."/>; const alert = data.safety_config.admin_email_alert; return <section className="mx-auto max-w-7xl space-y-6 px-4 py-7 md:px-8"><div><p className="text-sm font-semibold text-[#ea580c]">Local monitoring</p><h2 className="text-2xl font-bold">Safety overview</h2><p className="mt-1 text-sm text-[#786b65]">Events are logged by the existing LangGraph workflow. Conversation text is intentionally not shown here.</p></div><div className="grid gap-4 md:grid-cols-4"><Metric label="Processed turns" value={data.total_turns}/><Metric label="Simulated escalations" value={data.escalations}/><Metric label="Output validator" value={data.safety_config.validator}/><Metric label="Admin email" value={alert?.enabled ? "Ready" : "Not configured"}/></div><div className="card overflow-hidden"><div className="border-b border-[#f0e2d3] p-5"><h3 className="font-bold">Recent safety events</h3><p className="mt-1 text-xs text-[#786b65]">Emergency escalation is simulated. A configured prototype admin email contains no chat text.</p></div><div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead className="bg-[#fff9f5] text-xs uppercase tracking-wide text-[#786b65]"><tr><th className="p-4">Time</th><th className="p-4">Risk level</th><th className="p-4">Route</th><th className="p-4">Triggers</th><th className="p-4">Status</th></tr></thead><tbody>{data.events.map((event:any, index:number) => <tr className="border-t border-[#f0e2d3]" key={index}><td className="p-4 text-xs">{event.timestamp}</td><td className="p-4"><span className={`rounded-full px-2 py-1 text-xs font-bold ${event.risk_level >= 3 ? "bg-[#fff0ee] text-[#b54a3e]" : event.risk_level === 2 ? "bg-[#fff7df] text-[#946519]" : "bg-[#ffedd5] text-[#c2410c]"}`}>Level {event.risk_level}</span></td><td className="p-4">{event.route}</td><td className="p-4 text-xs">{event.triggers.join(", ") || "No rule trigger"}</td><td className="p-4">{event.escalated ? <span className="text-[#ae493d]">Simulated escalation</span> : "Logged"}</td></tr>)}</tbody></table></div></div></section>; }

function LlmPage({ onSave }: { onSave: (v:LlmConfig) => void }) { const [providers, setProviders] = useState<any[]>([]); const [models, setModels] = useState<string[]>([]); const [form, setForm] = useState({provider:"ollama", model:"qwen2.5:1.5b", endpoint:"http://localhost:11434/v1", api_key:""}); const [notice, setNotice] = useState(""); const [busy, setBusy] = useState(false);
  useEffect(() => { api<any[]>("/api/llm/providers").then(setProviders); api<LlmConfig>("/api/llm/config").then(c => setForm({provider:c.provider,model:c.model,endpoint:c.ollama_endpoint || "http://localhost:11434/v1",api_key:""})); }, []); useEffect(() => { if (!form.provider) return; api<{models:string[]}>(`/api/llm/models?provider=${form.provider}`).then(x => { setModels(x.models); if (!x.models.includes(form.model)) setForm(f => ({...f,model:x.models[0]})); }); }, [form.provider]);
  const submit = async (test=false) => { setBusy(true); setNotice(""); try { const path=test?"/api/llm/test-connection":"/api/llm/config"; const result = await api<any>(path,{method:"POST",body:JSON.stringify(form)}); if(!test) onSave(result); setNotice(test ? `Connection successful: ${result.preview}` : "Configuration saved. New conversations will use this provider."); setForm(f=>({...f,api_key:""})); } catch(e) { setNotice(e instanceof Error ? e.message : "Could not save configuration."); } finally { setBusy(false); } };
  return <section className="mx-auto max-w-3xl space-y-6 px-4 py-7 md:px-8"><div><p className="text-sm font-semibold text-[#ea580c]">Runtime configuration</p><h2 className="text-2xl font-bold">LLM configuration</h2><p className="mt-1 text-sm text-[#786b65]">Every provider uses the same independent safety screening, routing, templates, validation, and local logging.</p></div><div className="card p-5 md:p-7"><div className="grid gap-5 md:grid-cols-2"><label className="text-sm font-semibold">Provider<select value={form.provider} onChange={e=>setForm({...form,provider:e.target.value})} className="field mt-2 font-normal">{providers.map(p=><option key={p.id} value={p.id}>{p.label}</option>)}</select></label><label className="text-sm font-semibold">Model<select value={form.model} onChange={e=>setForm({...form,model:e.target.value})} className="field mt-2 font-normal">{models.map(m=><option key={m}>{m}</option>)}</select></label>{form.provider === "ollama" && <label className="text-sm font-semibold md:col-span-2">Local endpoint<input value={form.endpoint} onChange={e=>setForm({...form,endpoint:e.target.value})} className="field mt-2 font-normal"/></label>}{form.provider !== "ollama" && <label className="text-sm font-semibold md:col-span-2">API key<input type="password" value={form.api_key} onChange={e=>setForm({...form,api_key:e.target.value})} placeholder="Enter only to update the backend runtime" className="field mt-2 font-normal"/><span className="mt-1 block text-xs font-normal text-[#786b65]">Keys are never returned to the browser or stored in local storage.</span></label>}</div><div className="mt-7 flex flex-wrap gap-3"><button disabled={busy} onClick={()=>submit(true)} className="btn btn-quiet"><Zap size={16}/>{busy?"Testing…":"Test connection"}</button><button disabled={busy} onClick={()=>submit()} className="btn btn-primary"><Check size={16}/>Save configuration</button></div>{notice && <p className={`mt-5 rounded-xl p-3 text-sm ${notice.startsWith("Connection successful") || notice.startsWith("Configuration saved") ? "bg-[#ffedd5] text-[#9a3412]" : "bg-[#fff1ef] text-[#b2463b]"}`}>{notice}</p>}</div></section>; }

function TestsPage() { const [data,setData]=useState<any[]>([]); const [query,setQuery]=useState(""); const [category,setCategory]=useState("all"); useEffect(()=>{api<{cases:any[]}>("/api/evaluation/test-cases").then(x=>setData(x.cases)).catch(()=>{});},[]); const categories=useMemo(()=>[...new Set(data.map(x=>x.category))], [data]); const filtered=data.filter(x=>(category==="all"||x.category===category)&&JSON.stringify(x).toLowerCase().includes(query.toLowerCase())); return <section className="mx-auto max-w-7xl space-y-6 px-4 py-7 md:px-8"><div><p className="text-sm font-semibold text-[#ea580c]">Fictional data only</p><h2 className="text-2xl font-bold">Synthetic test cases</h2></div><div className="card p-4"><div className="flex flex-wrap gap-3"><input className="field max-w-sm" value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search test cases"/><select className="field w-52" value={category} onChange={e=>setCategory(e.target.value)}><option value="all">All categories</option>{categories.map(c=><option key={c}>{c}</option>)}</select></div></div><div className="card overflow-hidden"><div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead className="bg-[#fff9f5] text-xs uppercase tracking-wide text-[#786b65]"><tr><th className="p-4">ID</th><th className="p-4">Category</th><th className="p-4">Input</th><th className="p-4">Expected action</th></tr></thead><tbody>{filtered.map(c=><tr key={c.id} className="border-t border-[#f0e2d3]"><td className="p-4 font-semibold">{c.id}</td><td className="p-4"><span className="rounded-full bg-[#ffedd5] px-2 py-1 text-xs text-[#9a3412]">{c.category}</span></td><td className="max-w-lg p-4 text-[#786b65]">{c.turns.join(" → ")}</td><td className="p-4 font-semibold">{c.expected_action}</td></tr>)}</tbody></table></div></div></section>; }

function SettingsPage(){return <section className="mx-auto max-w-3xl px-4 py-7 md:px-8"><div className="card p-6"><Settings className="text-[#ea580c]"/><h2 className="mt-3 text-2xl font-bold">Application settings</h2><p className="mt-2 text-sm leading-6 text-[#786b65]">Theme preference is controlled in the header. Model configuration is available on its own page; safety rules remain read-only to preserve the approved workflow.</p><NavLink to="/llm" className="btn btn-primary mt-5">Open LLM configuration</NavLink></div></section>}
function AboutPage(){return <section className="mx-auto max-w-3xl space-y-5 px-4 py-7 md:px-8"><div className="card p-6"><FileText className="text-[#ea580c]"/><h2 className="mt-3 text-2xl font-bold">About MannSahara</h2><p className="mt-3 text-sm leading-7 text-[#786b65]">MannSahara is a university prototype for synthetic demonstrations. It uses a stateful LangGraph workflow: rules and an optional LLM classifier assess risk, a deterministic policy chooses the route, and fixed crisis/check-in templates plus output validation protect every reply.</p></div><div className="rounded-2xl border border-[#f6d6d0] bg-[#fff7f5] p-5 text-sm leading-6 text-[#874139]"><strong>Important:</strong> This is not a counsellor, doctor, or emergency service. It does not diagnose or contact anyone. Escalation in this prototype is simulated.</div></section>}
function Empty({title,text}:{title:string;text:string}){return <section className="grid min-h-[calc(100vh-76px)] place-items-center p-6"><div className="card max-w-md p-8 text-center"><Activity className="mx-auto text-[#ea580c]"/><h2 className="mt-3 text-xl font-bold">{title}</h2><p className="mt-2 text-sm leading-6 text-[#786b65]">{text}</p></div></section>}

export default function App(){const backend=useBackend(); return <AppShell config={backend.config} online={backend.online} onConfigChange={backend.setConfig}><Routes><Route path="/" element={<Navigate to="/chat" replace/>}/><Route path="/chat" element={<ChatPage/>}/><Route path="/safety" element={<SafetyPage/>}/><Route path="/evaluation" element={<EvaluationPage/>}/><Route path="/tests" element={<TestsPage/>}/><Route path="/llm" element={<LlmPage onSave={backend.setConfig}/>}/><Route path="/settings" element={<SettingsPage/>}/><Route path="/about" element={<AboutPage/>}/><Route path="*" element={<Navigate to="/chat" replace/>}/></Routes></AppShell>}
