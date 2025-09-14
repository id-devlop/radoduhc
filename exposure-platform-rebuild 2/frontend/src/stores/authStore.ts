
import { create } from 'zustand'
const API = import.meta.env.VITE_API_BASE || 'http://localhost:8080'

type State = { token: string|null, role: 'underwriter'|'cuo'|'admin' }
type Actions = { loginDemo: (role: string)=>Promise<void> }

export const useAuthStore = create<State & Actions>((set)=> ({
  token: null, role: 'underwriter',
  loginDemo: async (role: string='underwriter') => {
    const r = await fetch(`${API}/auth/demo-token?role=${role}`)
    const j = await r.json()
    set({ token: j.token, role: (role as any) })
  }
}))
