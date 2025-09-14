
import React, { useEffect, useState } from 'react'
import MetricsCard from '../components/MetricsCard'
import ScenarioRunner from '../components/ScenarioRunner'
import DeltaRiskPanel from '../components/DeltaRiskPanel'
import { api } from '../api/client'

export default function Dashboard(){
  const [conf,setConf]=useState<any>(null)
  const [summary,setSummary]=useState<any>({summary:[]})
  useEffect(()=>{ api('/config/effective').then(setConf); api('/exposure/summary').then(setSummary) },[])
  return <div className="grid md:grid-cols-3 gap-4">
    <MetricsCard title="Rules Version" value={conf?.metadata?.version||'—'} sub={conf?.metadata?.effective_from}/>
    <MetricsCard title="ROE Target" value={`${(conf?.targets?.min_roe*100||10).toFixed(0)}%`}/>
    <MetricsCard title="COR Target" value={`${(conf?.targets?.max_cor*100||90).toFixed(0)}%`}/>
    <div className="md:col-span-2 p-4 border rounded bg-white">
      <div className="font-semibold mb-2">Exposure Summary</div>
      <table className="w-full text-sm">
        <thead><tr><th className="text-left">LoB</th><th>Jurisdiction</th><th>Count</th><th className="text-right">TSI</th><th className="text-right">AAL</th><th className="text-right">PML</th></tr></thead>
        <tbody>
          {summary.summary.map((r:any,i:number)=>(
            <tr key={i} className="border-t">
              <td>{r.lob}</td><td className="text-center">{r.jurisdiction}</td><td className="text-center">{r.cnt}</td>
              <td className="text-right">${Number(r.tsi||0).toLocaleString()}</td>
              <td className="text-right">${Number(r.aal||0).toLocaleString()}</td>
              <td className="text-right">${Number(r.pml||0).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
    <ScenarioRunner/>
    <DeltaRiskPanel/>
  </div>
}
