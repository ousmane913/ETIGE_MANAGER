import { Link, usePage } from '@inertiajs/react'
import React from 'react'

const links = [{ href: '/', label: 'Tableau de bord' }, { href: '/projets/', label: 'Projets' }, { href: '/devis-independants/', label: 'Devis indépendants' }, { href: '/clients/', label: 'Clients' }, { href: '/journal-activite/', label: 'Journal d’activité' }]

// Pages racines qui n'ont pas besoin de bouton retour
const ROOT_PATHS = ['/', '/projets/', '/devis-independants/', '/clients/', '/journal-activite/']

export default function AppLayout({ children, back }: { children: React.ReactNode; back?: string | boolean }) {
  const page = usePage(); const url = page.url; const flash = (page.props as any).flash
  const [accountMenuOpen, setAccountMenuOpen] = React.useState(false)

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

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <aside className="fixed inset-y-0 hidden w-64 bg-slate-950 p-6 text-white lg:block">
        <Link href="/" className="mb-10 block text-xl font-black tracking-tight">ETIGE<span className="text-amber-400">.Manager</span></Link>
        <nav className="space-y-1">
          {links.map(link => <Link key={link.href} href={link.href} className={`block rounded-lg px-3 py-2 text-sm ${url === link.href ? 'bg-slate-800 text-amber-300' : 'text-slate-300 hover:bg-slate-900'}`}>{link.label}</Link>)}
        </nav>
        <div className="absolute bottom-6 text-xs text-slate-400"><a href="/deconnexion/">Se déconnecter</a></div>
      </aside>
      <main className="min-h-screen lg:ml-64">
        <header className="border-b border-slate-200 bg-white">
          <div className="flex items-center justify-between px-4 py-4 sm:px-10 sm:py-5">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-amber-600">Pilotage des opérations</p>
              <h1 className="text-base font-bold sm:text-lg">Gestion de projets ETIGE</h1>
            </div>
            <div className="relative shrink-0">
              <button
                type="button"
                aria-label="Menu du compte"
                aria-haspopup="menu"
                aria-expanded={accountMenuOpen}
                aria-controls="account-menu"
                onClick={() => setAccountMenuOpen(!accountMenuOpen)}
                className="h-9 w-9 rounded-full bg-slate-900 text-center text-sm font-bold leading-9 text-amber-300"
              >EM</button>
              {accountMenuOpen && <div id="account-menu" role="menu" className="absolute right-0 top-full z-50 mt-2 min-w-40 rounded-md border border-slate-200 bg-white p-1 text-sm shadow-lg">
                <a href="/deconnexion/" role="menuitem" className="block rounded px-3 py-2 font-semibold text-red-700 hover:bg-red-50">Se déconnecter</a>
              </div>}
            </div>
          </div>
          <nav className="flex gap-2 overflow-x-auto px-4 pb-3 lg:hidden">
            {links.map(link => <Link key={link.href} href={link.href} className={`shrink-0 rounded-lg px-3 py-2 text-sm ${url === link.href ? 'bg-slate-900 text-amber-300' : 'bg-slate-100 text-slate-700'}`}>{link.label}</Link>)}
          </nav>
        </header>
        {flash?.messages?.length > 0 && <div className="fixed right-4 top-4 z-50 max-w-[calc(100%-2rem)] rounded-lg border border-emerald-200 bg-emerald-50 px-5 py-3 text-sm font-semibold text-emerald-800 shadow-lg" role="status">{flash.messages[0].message}</div>}
        <div className="mx-auto max-w-7xl p-4 sm:p-10">
          {showBack && <button onClick={goBack} className="mb-6 flex items-center gap-2 text-sm font-semibold text-slate-500 transition-colors hover:text-amber-700"><span className="flex h-7 w-7 items-center justify-center rounded-full border border-slate-200 bg-white text-base leading-none shadow-sm">←</span>Retour</button>}
          {children}
        </div>
      </main>
    </div>
  )
}

