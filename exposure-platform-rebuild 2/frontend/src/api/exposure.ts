
import { api } from './client'
export const getSummary = ()=> api('/exposure/summary')
export const getGeo = ()=> api('/exposure/by-geo')
export const postExposure = (payload:any)=> api('/exposure',{method:'POST', body: JSON.stringify(payload)})
