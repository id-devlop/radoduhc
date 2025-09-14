
const API = import.meta.env.VITE_API_BASE || 'http://localhost:8080'
export async function api(path: string, init: RequestInit = {}){
  const headers = {'Content-Type':'application/json', ...(init.headers||{})}
  const resp = await fetch(`${API}${path}`, { ...init, headers })
  if(!resp.ok) throw new Error(`${resp.status} ${resp.statusText}`)
  const ctype = resp.headers.get('content-type')||''
  return ctype.includes('application/json') ? await resp.json() : await resp.text()
}
