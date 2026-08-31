import AppLayout from '../layouts/AppLayout'
import { Link } from '@inertiajs/react'
import Status from '../components/Status'
import { useState } from 'react'

function BarChart({ data }: { data: { label: string; created: number; closed: number }[] }) {
    const maxVal = Math.max(...data.flatMap(d => [d.created, d.closed]), 1)
    const chartH = 180
    const barW = 14
    const gap = 4
    const groupW = barW * 2 + gap + 16
    const svgW = data.length * groupW + 40
    const padLeft = 36
    const padBottom = 32
    const gridLines = [0, 0.25, 0.5, 0.75, 1]
    return (
        <div className="overflow-x-auto">
            <svg width={svgW + padLeft} height={chartH + padBottom + 16} style={{ display: 'block', minWidth: '100%' }}>
                {gridLines.map((ratio, i) => {
                    const y = 8 + chartH - ratio * chartH
                    return (
                        <g key={i}>
                            <line x1={padLeft} x2={svgW + padLeft} y1={y} y2={y} stroke="#e2e8f0" strokeWidth={1} />
                            <text x={padLeft - 4} y={y + 4} textAnchor="end" fontSize={9} fill="#94a3b8">{Math.round(ratio * maxVal)}</text>
                        </g>
                    )
                })}
                {data.map((d, i) => {
                    const x = padLeft + i * groupW + 8
                    const createdH = Math.max((d.created / maxVal) * chartH, d.created > 0 ? 2 : 0)
                    const closedH = Math.max((d.closed / maxVal) * chartH, d.closed > 0 ? 2 : 0)
                    const baseY = 8 + chartH
                    return (
                        <g key={i}>
                            <rect x={x} y={baseY - createdH} width={barW} height={createdH} fill="#f59e0b" rx={3}><title>{d.created} créé(s)</title></rect>
                            <rect x={x + barW + gap} y={baseY - closedH} width={barW} height={closedH} fill="#10b981" rx={3}><title>{d.closed} clôturé(s)</title></rect>
                            <text x={x + barW + gap / 2} y={baseY + 14} textAnchor="middle" fontSize={9} fill="#64748b">{d.label}</text>
                        </g>
                    )
                })}
            </svg>
            <div className="mt-2 flex gap-5 text-xs text-slate-500">
                <span className="flex items-center gap-1.5"><span className="inline-block h-3 w-3 rounded-sm bg-amber-400" />Créés</span>
                <span className="flex items-center gap-1.5"><span className="inline-block h-3 w-3 rounded-sm bg-emerald-500" />Clôturés</span>
            </div>
        </div>
    )
}

export default function Dashboard({ metrics, recentProjects, user, projectsEvolution }: any) {
    const [period, setPeriod] = useState<'monthly' | 'quarterly' | 'semesterly'>('monthly')
    const cards = [['Clients', metrics.clients, '👥'], ['Projets', metrics.projects, '📁'], ['Devis à traiter', metrics.quotesPending, '📋'], ['Chantiers actifs', metrics.activeSites, '🏗️']]
    const tabs: { key: 'monthly' | 'quarterly' | 'semesterly'; label: string }[] = [{ key: 'monthly', label: 'Mensuel' }, { key: 'quarterly', label: 'Trimestriel' }, { key: 'semesterly', label: 'Semestriel' }]
    const chartData = projectsEvolution?.[period] || []
    return (
        <AppLayout>
            <div className="mb-8 flex items-end justify-between">
                <div><h2 className="text-3xl font-bold">Bonjour, {user.name}</h2><p className="mt-1 text-slate-500">Vue d'ensemble des opérations en cours.</p></div>
                <Link href="/projets/nouveau/" className="btn-primary">+ Nouveau projet</Link>
            </div>
            <section className="grid gap-4 md:grid-cols-4">
                {cards.map(([title, value, icon]) => (
                    <div className="card" key={title as string}>
                        <p className="text-2xl">{icon}</p>
                        <p className="mt-2 text-sm text-slate-500">{title}</p>
                        <p className="mt-1 text-3xl font-bold">{value}</p>
                    </div>
                ))}
            </section>
            <section className="card mt-7">
                <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
                    <h3 className="font-bold">Évolution des projets</h3>
                    <div className="flex rounded-lg border border-slate-200 p-0.5 text-sm">
                        {tabs.map(tab => (
                            <button key={tab.key} onClick={() => setPeriod(tab.key)} className={`rounded-md px-3 py-1 font-medium transition-colors ${period === tab.key ? 'bg-amber-500 text-white' : 'text-slate-500 hover:text-slate-700'}`}>{tab.label}</button>
                        ))}
                    </div>
                </div>
                <BarChart data={chartData} />
            </section>
            <section className="card mt-7">
                <div className="mb-4 flex justify-between"><h3 className="font-bold">Derniers projets</h3><Link href="/projets/" className="text-sm font-semibold text-amber-700">Voir tous</Link></div>
                <div className="divide-y">
                    {recentProjects.map((p: any) => (
                        <Link href={`/projets/${p.id}/`} className="flex items-center justify-between py-3 hover:bg-slate-50" key={p.id}>
                            <div><p className="font-semibold">{p.name}</p><p className="text-sm text-slate-500">{p.reference} {p.client}</p></div>
                            <Status value={p.status} />
                        </Link>
                    ))}
                    {!recentProjects.length && <p className="py-5 text-sm text-slate-500">Aucun projet pour le moment.</p>}
                </div>
            </section>
        </AppLayout>
    )
}

