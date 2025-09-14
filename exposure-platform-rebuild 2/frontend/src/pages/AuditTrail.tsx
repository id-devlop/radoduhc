
import React, { useEffect, useState } from 'react'
import { api } from '../api/client'

export default function AuditTrail(){
  const [rows,setRows]=useState<any[]>([])
  useEffect(()=>{ api('/audit/history?limit=50').then((r:any)=>setRows(r.events||[])) },[])
  return <div className="space-y-2">
    <div className="text-lg font-semibold">Audit Trail</div>
    <table className="w-full text-sm bg-white rounded border">
      <thead><tr><th>ID</th><th>Type</th><th>User</th><th>Role</th><th>Timestamp</th></tr></thead>
      <tbody>
        {rows.map(r=>(
          <tr key={r.id} className="border-t">
            <td>{r.id}</td><td>{r.type}</td><td>{r.user}</td><td>{r.role}</td><td>{r.timestamp}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
}
