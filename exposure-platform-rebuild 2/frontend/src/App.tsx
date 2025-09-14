
import React, { useEffect, useState } from 'react'
import { useAuthStore } from './stores/authStore'
import Dashboard from './pages/Dashboard'
import AuditTrail from './pages/AuditTrail'
import ExposureMap from './pages/ExposureMap'
import Correlation from './pages/Correlation'
import Capital from './pages/Capital'
import ConfigurationPage from './pages/Configuration'

export default function App(){
  const { token, loginDemo } = useAuthStore()
  const [tab,setTab]=useState<'dash'|'map'|'corr'|'cap'|'conf'|'audit'>('dash')
  useEffect(()=>{ if(!token) loginDemo('cuo') },[])
  return (
    <div className="p-6 space-y-4">
      <div className="flex gap-3">
        <button onClick={()=>setTab('dash')}>Dashboard</button>
        <button onClick={()=>setTab('map')}>Exposure Map</button>
        <button onClick={()=>setTab('corr')}>Correlation</button>
        <button onClick={()=>setTab('cap')}>Capital</button>
        <button onClick={()=>setTab('conf')}>Configuration</button>
        <button onClick={()=>setTab('audit')}>Audit</button>
      </div>
      {tab==='dash'&&<Dashboard/>}
      {tab==='map'&&<ExposureMap/>}
      {tab==='corr'&&<Correlation/>}
      {tab==='cap'&&<Capital/>}
      {tab==='conf'&&<ConfigurationPage/>}
      {tab==='audit'&&<AuditTrail/>}
    </div>
  )
}
