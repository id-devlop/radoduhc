
import { api } from './client'
export const getLibrary = ()=> api('/scenario/library')
export const runScenario = (payload:any)=> api('/scenario/run',{method:'POST', body: JSON.stringify(payload)})
