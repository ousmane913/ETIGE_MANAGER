import AppLayout from '../../layouts/AppLayout'
import { Link, useForm } from '@inertiajs/react'

function ClientRow({ client }: any) {
    const { post, processing } = useForm({})
    const deleteClient = (event: React.FormEvent) => {
        event.preventDefault()
        if (window.confirm(`Souhaitez-vous supprimer le client « ${client.company_name} » ?`)) post(`/clients/${client.id}/supprimer/`)
    }
    return <tr className="border-t" key={client.id}><td className="p-4 font-semibold">{client.company_name}</td><td className="p-4">{client.contact_name}</td><td className="p-4">{client.email || '—'}</td><td className="p-4">{client.phone}</td><td className="p-4"><div className="flex flex-wrap gap-2"><Link href={`/clients/${client.id}/modifier/`} className="rounded-lg border border-amber-200 px-3 py-2 text-sm font-semibold text-amber-700 hover:bg-amber-50">Modifier</Link><form onSubmit={deleteClient}><button type="submit" disabled={processing} className="rounded-lg border border-red-200 px-3 py-2 text-sm font-semibold text-red-700 hover:bg-red-50 disabled:opacity-50">{processing ? 'Suppression…' : 'Supprimer'}</button></form></div></td></tr>
}

export default function Clients({ clients }: any) { return <AppLayout><div className="mb-7 flex items-center justify-between"><div><h2 className="text-3xl font-bold">Clients</h2><p className="text-slate-500">Maîtres d’ouvrage et contacts.</p></div><Link href="/clients/nouveau/" className="btn-primary">+ Nouveau client</Link></div><div className="card overflow-x-auto p-0"><table className="w-full min-w-[820px] text-left text-sm"><thead className="bg-slate-50 text-slate-500"><tr><th className="p-4">Société</th><th className="p-4">Contact</th><th className="p-4">Email</th><th className="p-4">Téléphone</th><th className="p-4">Actions</th></tr></thead><tbody>{clients.map((client: any) => <ClientRow key={client.id} client={client} />)}{!clients.length && <tr><td className="p-5 text-slate-500" colSpan={5}>Aucun client enregistré.</td></tr>}</tbody></table></div></AppLayout> }
