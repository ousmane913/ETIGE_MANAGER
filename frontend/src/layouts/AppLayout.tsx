import { Link, usePage } from '@inertiajs/react'
import React from 'react'

const links = [{ href: '/', label: 'Tableau de bord' }, { href: '/projets/', label: 'Projets' }, { href: '/clients/', label: 'Clients' }]
export default function AppLayout({ children }: { children: React.ReactNode }) {
  const page = usePage(); const url = page.url
  return <div className="min-h-screen bg-slate-50 text-slate-900"><aside className="fixed inset-y-0 w-64 bg-slate-950 p-6 text-white"><Link href="/" className="mb-10 block text-xl font-black tracking-tight">BTP<span className="text-amber-400">.Manager</span></Link><nav className="space-y-1">{links.map(l => <Link key={l.href} href={l.href} className={`block rounded-lg px-3 py-2 text-sm ${url === l.href ? 'bg-slate-800 text-amber-300' : 'text-slate-300 hover:bg-slate-900'}`}>{l.label}</Link>)}</nav><div className="absolute bottom-6 text-xs text-slate-400"><a href="/deconnexion/">Se déconnecter</a></div></aside><main className="ml-64 min-h-screen"><header className="flex items-center justify-between border-b border-slate-200 bg-white px-10 py-5"><div><p className="text-xs font-semibold uppercase tracking-wider text-amber-600">Pilotage des opérations</p><h1 className="text-lg font-bold">Gestion de projets BTP</h1></div><div className="h-9 w-9 rounded-full bg-slate-900 text-center leading-9 text-sm font-bold text-amber-300">BM</div></header><div className="mx-auto max-w-7xl p-10">{children}</div></main></div>
}
