import AppLayout from '../../layouts/AppLayout'
import { Link, useForm } from '@inertiajs/react'

function SendQuoteButton({ quote }: any) {
    const { post, processing } = useForm({ email: quote.clientEmail || '' })
    return (
        <form onSubmit={(event) => { event.preventDefault(); post(`/devis-independants/${quote.id}/envoyer-email/`) }}>
            <button className="font-semibold text-blue-700 disabled:opacity-50" type="submit" disabled={processing}>Envoyer</button>
        </form>
    )
}

export default function IndependentQuotes({ quotes, searchQuery }: any) {
    return (
        <AppLayout>
            <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
                <div>
                    <h2 className="text-3xl font-bold">Devis indépendants</h2>
                    <p className="mt-1 text-slate-500">Devis non liés à un projet.</p>
                </div>
                <Link href="/devis-independants/nouveau/" className="btn-primary">+ Nouveau devis</Link>
            </div>
            <form method="get" className="mb-5 flex gap-3">
                <input className="input max-w-md" name="q" defaultValue={searchQuery} placeholder="Rechercher un devis ou un client" />
                <button className="btn-muted" type="submit">Rechercher</button>
            </form>
            <div className="card overflow-x-auto">
                <table className="w-full min-w-[720px] text-left text-sm">
                    <thead>
                        <tr className="border-b border-slate-200 text-slate-500">
                            <th className="p-3">Devis</th>
                            <th className="p-3">Client</th>
                            <th className="p-3">Montant</th>
                            <th className="p-3">Statut</th>
                            <th className="p-3 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {quotes.map((quote: any) => (
                            <tr key={quote.id} className="border-b border-slate-100">
                                <td className="p-3 font-semibold">{quote.number}</td>
                                <td className="p-3">{quote.client}</td>
                                <td className="p-3">{Number(quote.amount).toLocaleString('fr-FR')} FCFA</td>
                                <td className="p-3"><span className={`rounded-full px-3 py-1 text-xs font-semibold ${quote.status === 'ACCEPTED' ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>{quote.status === 'ACCEPTED' ? 'Accepté' : 'Refusé'}</span></td>
                                <td className="p-3 text-right">
                                    <div className="flex justify-end gap-3">
                                        <Link href={`/devis-independants/${quote.id}/`} className="font-semibold text-amber-700">Modifier</Link>
                                        <a href={`/devis-independants/${quote.id}/pdf/`} target="_blank" rel="noreferrer" className="font-semibold text-slate-700">PDF</a>
                                        <SendQuoteButton quote={quote} />
                                    </div>
                                </td>
                            </tr>
                        ))}
                        {!quotes.length && <tr><td className="p-6 text-center text-slate-500" colSpan={5}>Aucun devis indépendant.</td></tr>}
                    </tbody>
                </table>
            </div>
        </AppLayout>
    )
}