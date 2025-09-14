
import React, { useEffect, useState } from 'react'
import { api } from '../api/client'
export default function ConfigurationPage(){
  const [conf,setConf]=useState<any>(null)
  useEffect(()=>{ api('/config/effective').then(setConf) },[])
  return <div className="space-y-2">
    <div className="text-lg font-semibold">Rules in Effect</div>
    <pre className="bg-gray-50 p-3 rounded text-xs">{JSON.stringify(conf?.classes, null, 2)}</pre>
  </div>
}
