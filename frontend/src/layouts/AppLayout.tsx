import { Link, usePage } from '@inertiajs/react'
import React from 'react'

const links = [{ href: '/', label: 'Tableau de bord' }, { href: '/projets/', label: 'Projets' }, { href: '/clients/', label: 'Clients' }]

// Pages racines qui n'ont pas besoin de bouton retour
const ROOT_PATHS = ['/', '/projets/', '/clients/']

export default function AppLayout({ children, back }: { children: React.ReactNode; back?: string | boolean }) {
  const page = usePage(); const url = page.url; const flash = (page.props as any).flash

  // Affiche le bouton retour si :
  // - prop back est passé explicitement (string = URL cible, true = history.back)
  // - ou si l'URL actuelle n'est pas une page racine
  const isRoot = ROOT_PATHS.includes(url)
  const showBack = back !== false && (back || !isRoot)

  function goBack(e: React.MouseEvent) {
    e.preventDefault()
    if (typeof back === 'string') {
      window.location.href = back
    } else {
      window.history.back()
    }
  }

  return <div className="min-h-screen bg-slate-50 text-slate-900"><aside className="fixed inset-y-0 hidden w-64 bg-slate-950 p-6 text-white lg:block"><Link href="/" className="mb-10 block text-xl font-black tracking-tight">ETIGE<span className="text-amber-400">.Manager</span></Link><nav className="space-y-1">{links.map(l => <Link key={l.href} href={l.href} className={`block rounded-lg px-3 py-2 text-sm ${url === l.href ? 'bg-slate-800 text-amber-300' : 'text-slate-300 hover:bg-slate-900'}`}>{l.label}</Link>)}</nav><div className="absolute bottom-6 text-xs text-slate-400"><a href="/deconnexion/">Se déconnecter</a></div></aside><main className="min-h-screen lg:ml-64"><header className="border-b border-slate-200 bg-white"><div className="flex items-center justify-between px-4 py-4 sm:px-10 sm:py-5"><div><p className="text-xs font-semibold uppercase tracking-wider text-amber-600">Pilotage des opérations</p><h1 className="text-base font-bold sm:text-lg">Gestion de projets ETIGE</h1></div><div className="h-9 w-9 shrink-0 rounded-full bg-slate-900 text-center leading-9 text-sm font-bold text-amber-300">EM</div></div><nav className="flex gap-2 overflow-x-auto px-4 pb-3 lg:hidden">{links.map(l => <Link key={l.href} href={l.href} className={`shrink-0 rounded-lg px-3 py-2 text-sm ${url === l.href ? 'bg-slate-900 text-amber-300' : 'bg-slate-100 text-slate-700'}`}>{l.label}</Link>)}</nav></header>{flash?.messages?.length > 0 && <div className="fixed right-4 top-4 z-50 max-w-[calc(100%-2rem)] rounded-lg border border-emerald-200 bg-emerald-50 px-5 py-3 text-sm font-semibold text-emerald-800 shadow-lg" role="status">{flash.messages[0].message}</div>}<div className="mx-auto max-w-7xl p-4 sm:p-10">{showBack && <button onClick={goBack} className="mb-6 flex items-center gap-2 text-sm font-semibold text-slate-500 transition-colors hover:text-amber-700"><span className="flex h-7 w-7 items-center justify-center rounded-full border border-slate-200 bg-white text-base leading-none shadow-sm">←</span>Retour</button>}{children}</div></main></div>
}

