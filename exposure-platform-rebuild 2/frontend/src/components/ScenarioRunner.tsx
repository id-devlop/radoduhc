
import React, { useEffect, useState } from 'react'
import { getLibrary, runScenario } from '../api/scenario'
import { runMC } from '../api/simulate'

type Treaty = { type: 'AGG_XOL' | 'STOP_LOSS', attachment: number, limit: number, reinstatements: number }

export default function ScenarioRunner(){
  const [lib,setLib]=useState<any[]>([])
  const [sel,setSel]=useState<string>('')
  const [out,setOut]=useState<any|null>(null)
  const [mc,setMc]=useState<any|null>(null)
  const [treaties, setTreaties] = useState<Treaty[]>([{ type:'AGG_XOL', attachment: 5_000_000, limit: 20_000_000, reinstatements: 1 }])
  const [copula, setCopula] = useState<string>('independent')

  useEffect(()=>{ getLibrary().then((r:any)=>{setLib(r.scenarios); if(r.scenarios[0]) setSel(r.scenarios[0].id)}) },[])

  const onScenario = async ()=>{
    const res = await runScenario({ id: sel, total: 2_000_000_000 })
    setOut(res)
  }
  const onMC = async ()=>{
    const res = await runMC({ trials: 200000, lam: 0.7, sev_mean: 14.0, sev_sd: 1.15, tiv: 2_000_000_000, treaties, copula })
    setMc(res)
  }

  const updateTreaty = (idx:number, patch:Partial<Treaty>)=>{
    const next = treaties.slice(); next[idx] = { ...next[idx], ...patch }; setTreaties(next)
  }

  return <div className="p-4 border rounded bg-white space-y-3">
    <div className="font-semibold">Scenario Runner</div>
    <div className="flex gap-2 items-center">
      <select value={sel} onChange={e=>setSel(e.target.value)} className="border p-2 rounded">
        {lib.map((s:any)=><option key={s.id} value={s.id}>{s.name}</option>)}
      </select>
      <button className="px-3 py-2 bg-blue-600 text-white rounded" onClick={onScenario}>Run</button>
    </div>
    {out && <div className="text-sm">Loss: ${'{'}Math.round(out.portfolio_loss).toLocaleString(){'}'} ({'{'}out.capital_pct{'}'}% capital)</div>}

    <div className="pt-3 border-t">
      <div className="font-semibold mb-2">Treaties</div>
      {treaties.map((t,i)=>(
        <div key={i} className="grid grid-cols-5 gap-2 items-center mb-2">
          <select value={t.type} onChange={e=>updateTreaty(i,{type: e.target.value as any})} className="border p-2 rounded">
            <option value="AGG_XOL">AGG_XOL</option>
            <option value="STOP_LOSS">STOP_LOSS</option>
          </select>
          <input className="border p-2 rounded" type="number" value={t.attachment} onChange={e=>updateTreaty(i,{attachment: parseFloat(e.target.value)})} placeholder="Attachment"/>
          <input className="border p-2 rounded" type="number" value={t.limit} onChange={e=>updateTreaty(i,{limit: parseFloat(e.target.value)})} placeholder="Limit"/>
          <input className="border p-2 rounded" type="number" value={t.reinstatements} onChange={e=>updateTreaty(i,{reinstatements: parseInt(e.target.value||'0')})} placeholder="Reinstatements"/>
          <button className="px-2 py-2 bg-gray-100 rounded" onClick={()=>setTreaties([...treaties, {type:'AGG_XOL', attachment: 10_000_000, limit: 20_000_000, reinstatements:0}])}>+ Add</button>
        </div>
      ))}
      <div className="mt-2 flex items-center gap-2">
        <label className="text-sm">Copula:</label>
        <select value={copula} onChange={e=>setCopula(e.target.value)} className="border p-2 rounded">
          <option value="independent">independent</option>
          <option value="t-copula">t-copula</option>
        </select>
      </div>
    </div>

    <div className="pt-3 border-t">
      <div className="font-semibold mb-2">Monte Carlo (live)</div>
      <button className="px-3 py-2 bg-green-600 text-white rounded" onClick={onMC}>Run MC</button>
      {mc && <div className="text-sm mt-2 space-y-1">
        <div>Trials: { '{'}mc.trials{'}'}</div>
        <div>Mean Net: ${'{'}(mc.net_mean||0).toLocaleString(){'}'}</div>
        <div>VaR99: ${'{'}(mc.var99||0).toLocaleString(){'}'}</div>
        <div>TVaR99: ${'{'}(mc.tvar99||0).toLocaleString(){'}'}</div>
        <div>Tail Copula Index: { '{'}mc.tail_copula_index ?? '—'{'}'}</div>
      </div>}
    </div>
  </div>
}
