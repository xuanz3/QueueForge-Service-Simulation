import { useEffect, useState } from "react";
type Status = { service:string; version:string; status:string; database:string };
type State = {kind:"loading"}|{kind:"ready";data:Status}|{kind:"error";message:string};
const api = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:18086";
export default function App() {
  const [state,setState]=useState<State>({kind:"loading"});
  useEffect(()=>{ const c=new AbortController(); fetch(`${api}/api/system/status`,{signal:c.signal}).then(r=>{if(!r.ok)throw new Error(`HTTP ${r.status}`);return r.json()}).then((d:Status)=>setState({kind:"ready",data:d})).catch((e:unknown)=>{if(!c.signal.aborted)setState({kind:"error",message:e instanceof Error?e.message:"Unknown error"})}); return()=>c.abort();},[]);
  return <main><p className="eyebrow">SERVICE OPERATIONS SIMULATION</p><h1>QueueForge</h1><p className="intro">Test staffing assumptions with reproducible simulation evidence before changing real operations.</p><section className={`status ${state.kind}`}><strong>{state.kind==="ready"?"Foundation ready":state.kind==="loading"?"Checking local system":"Connection requires attention"}</strong><span>{state.kind==="ready"?`API ${state.data.version} · PostgreSQL ${state.data.database}`:state.kind==="error"?state.message:"Validating Java and PostgreSQL"}</span></section><div className="grid">{[["C++20","Deterministic simulation engine"],["Python","Repeated experiments and reports"],["Java","Lifecycle and persistence"],["React","Scenario and result interface"]].map(([a,b])=><article key={a}><small>PLANNED RESPONSIBILITY</small><h2>{a}</h2><p>{b}</p></article>)}</div></main>;
}
