
import React, { useEffect, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

export default function ExposureHeatmap({geo}:{geo:any}){
  const ref = useRef<HTMLDivElement>(null)
  useEffect(()=>{
    if(!ref.current) return
    const map = L.map(ref.current).setView([20,0], 2)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 19}).addTo(map)
    const style = (f:any)=>({radius: 6, color:'#2563eb'})
    const layer = L.geoJSON(geo as any, {
      pointToLayer: (feature, latlng) => L.circleMarker(latlng, style(feature))
    })
    layer.addTo(map)
    return ()=> { map.remove() }
  },[geo])
  return <div ref={ref} style={{height: 420}} />
}
