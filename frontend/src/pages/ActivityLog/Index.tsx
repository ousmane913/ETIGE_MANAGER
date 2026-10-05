import AppLayout from '../../layouts/AppLayout'
import { useForm } from '@inertiajs/react'

export default function ActivityLog({ activities, searchQuery, canDeleteActivities }: any) {
    const { post, processing } = useForm({})
    const clearActivityLog = (event: React.FormEvent) => {
        event.preventDefault()
        if (window.confirm('Voulez-vous vraiment vider tout le journal d’activité ? Cette action est irréversible.')) {
            post('/journal-activite/supprimer/')
        }
    }
    const deleteActivity = (event: React.FormEvent, activity: any) => {
        event.preventDefault()
        if (window.confirm(`Supprimer cette activité de ${activity.user} ? Cette action est irréversible.`)) {
            post(`/journal-activite/${activity.id}/supprimer/`)
        }
    }

    return (
        <AppLayout>
            <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
                <div>
                    <h2 className="text-3xl font-bold">Journal d'activité</h2>
                    <p className="mt-1 text-slate-500">Historique des actions effectuées dans l'application.</p>
                </div>
                {canDeleteActivities && <form onSubmit={clearActivityLog}>
                    <button type="submit" disabled={processing} className="btn-muted border-red-200 text-red-700 hover:bg-red-50 disabled:opacity-50">
                        {processing ? 'Suppression…' : 'Vider le journal'}
                    </button>
                </form>}
            </div>
            <form method="get" className="mb-5 flex gap-3">
                <input className="input max-w-md" name="q" defaultValue={searchQuery} placeholder="Rechercher une action, un utilisateur..." />
                <button className="btn-muted" type="submit">Rechercher</button>
            </form>
            <div className="card overflow-x-auto">
                <table className="w-full min-w-[780px] text-left text-sm">
                    <thead>
                        <tr className="border-b border-slate-200 text-slate-500">
                            <th className="p-3">Date</th>
                            <th className="p-3">Utilisateur</th>
                            <th className="p-3">Action</th>
                            <th className="p-3">Détail</th>
                            <th className="p-3">Projet</th>
                            {canDeleteActivities && <th className="p-3"></th>}
                        </tr>
                    </thead>
                    <tbody>
                        {activities.map((activity: any) => (
                            <tr key={activity.id} className="border-b border-slate-100">
                                <td className="p-3 whitespace-nowrap">{new Date(activity.date).toLocaleString('fr-FR')}</td>
                                <td className="p-3 font-semibold">{activity.user}</td>
                                <td className="p-3">{activity.action}</td>
                                <td className="p-3">{activity.description}</td>
                                <td className="p-3">{activity.project || '-'}</td>
                                {canDeleteActivities && <td className="p-3">
                                    <form onSubmit={(event) => deleteActivity(event, activity)}>
                                        <button type="submit" disabled={processing} className="rounded-lg border border-red-200 px-3 py-1.5 text-xs font-semibold text-red-700 hover:bg-red-50 disabled:opacity-50">
                                            Supprimer
                                        </button>
                                    </form>
                                </td>}
                            </tr>
                        ))}
                        {!activities.length && <tr><td className="p-6 text-center text-slate-500" colSpan={canDeleteActivities ? 6 : 5}>Aucune activité enregistrée.</td></tr>}
                    </tbody>
                </table>
            </div>
        </AppLayout>
    )
}
