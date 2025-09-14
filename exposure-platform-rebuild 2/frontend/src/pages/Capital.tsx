
import React, { useEffect, useState } from 'react'
import { api } from '../api/client'
export default function Capital(){
  const [curve,setCurve]=useState<any>(null)
  useEffect(()=>{ api('/ecm/pull').then(setCurve) },[])
  return <div className="space-y-2">
    <div className="text-lg font-semibold">Economic Capital</div>
    <pre className="bg-gray-50 p-3 rounded text-xs">{JSON.stringify(curve,null,2)}</pre>
  </div>
}
