import AppLayout from '../../layouts/AppLayout'

export default function ActivityLog({ activities, searchQuery }: any) {
    return (
        <AppLayout>
            <div className="mb-8">
                <h2 className="text-3xl font-bold">Journal d'activité</h2>
                <p className="mt-1 text-slate-500">Historique des actions effectuées dans l'application.</p>
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
                            </tr>
                        ))}
                        {!activities.length && <tr><td className="p-6 text-center text-slate-500" colSpan={5}>Aucune activité enregistrée.</td></tr>}
                    </tbody>
                </table>
            </div>
        </AppLayout>
    )
}
