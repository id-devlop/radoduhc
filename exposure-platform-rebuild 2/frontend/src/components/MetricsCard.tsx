
import React from 'react'
export default function MetricsCard({title,value,sub}:{title:string,value:string|number,sub?:string}){
  return <div className="p-4 rounded border bg-white">
    <div className="text-sm text-gray-500">{title}</div>
    <div className="text-2xl font-semibold">{value}</div>
    {sub && <div className="text-xs text-gray-400">{sub}</div>}
  </div>
}
