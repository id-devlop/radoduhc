
import React, { useState } from 'react'
import { api } from '../api/client'

export default function Correlation(){
  const [out,setOut]=useState<any|null>(null)
  const sample = { series: { property:[1,2,3,4,5], marine:[2,3,3,5,6], casualty:[1,1,2,3,5] } }
  return <div className="space-y-3">
    <div className="text-lg font-semibold">Correlation (Pearson)</div>
    <button className="px-3 py-2 bg-blue-600 text-white rounded" onClick={async()=>{
      const r = await api('/correlation/estimate',{method:'POST', body: JSON.stringify(sample) })
      setOut(r)
    }}>Estimate</button>
    {out && <pre className="bg-gray-50 p-3 rounded text-xs">{JSON.stringify(out,null,2)}</pre>}
  </div>
}
