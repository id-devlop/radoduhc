
import React, { useEffect, useState } from 'react'
import ExposureHeatmap from '../components/ExposureHeatmap'
import { getGeo } from '../api/exposure'

export default function ExposureMap(){
  const [geo,setGeo]=useState<any>({"type":"FeatureCollection","features":[]})
  useEffect(()=>{ getGeo().then(setGeo) },[])
  return <div className="space-y-2">
    <div className="text-lg font-semibold">Exposure Map</div>
    <ExposureHeatmap geo={geo} />
  </div>
}
