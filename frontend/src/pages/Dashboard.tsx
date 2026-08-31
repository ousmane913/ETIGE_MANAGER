import AppLayout from '../layouts/AppLayout'
import { Link } from '@inertiajs/react'
import Status from '../components/Status'

export default function Dashboard({ metrics, recentProjects, user }: any) {
    const cards = [['Clients', metrics.clients, '👥'], ['Projets', metrics.projects, '📁'], ['Devis à traiter', metrics.quotesPending, '📋'], ['Chantiers actifs', metrics.activeSites, '🏗️']]
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
