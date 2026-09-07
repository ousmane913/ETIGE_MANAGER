import AppLayout from '../../layouts/AppLayout'
import { Link, useForm } from '@inertiajs/react'
import Status from '../../components/Status'
import { useState } from 'react'

function Step({ title, done, href, text, pdfHref, onSendEmail, quoteExists, planningExists, planningPdfHref }: any) {
    const downloadHref = pdfHref || (title.includes('Devis') ? href.replace('/devis/', '/devis/pdf/') : null)
    return (
        <div className={`rounded-xl border p-4 transition ${done ? 'border-emerald-200 bg-emerald-50' : 'border-slate-200 bg-white'}`}>
            <div className="flex items-center justify-between">
                <div>
                    <p className="font-bold text-slate-900">{title}</p>
                    <p className="mt-1 text-sm text-slate-500">{text}</p>
                </div>
                <span className={`text-lg font-bold ${done ? 'text-emerald-600' : 'text-slate-300'}`}>
                    {done ? '✓' : '○'}
                </span>
            </div>
            <div className="mt-4 flex flex-wrap items-center gap-4">
                <Link href={href} className="text-sm font-semibold text-amber-700 hover:text-amber-800">
                    {done ? 'Mettre à jour' : 'Renseigner'} →
                </Link>
                {downloadHref && quoteExists && (
                    <a href={downloadHref} target="_blank" rel="noreferrer" className="text-sm font-semibold text-slate-700 hover:text-slate-900">
                        📄 Télécharger le PDF
                    </a>
                )}
                {planningPdfHref && planningExists && (
                    <a href={planningPdfHref} target="_blank" rel="noreferrer" className="text-sm font-semibold text-indigo-700 hover:text-indigo-900">
                        📄 Télécharger le Planning (PDF Client)
                    </a>
                )}
                {onSendEmail && quoteExists && (
                    <button
                        type="button"
                        onClick={onSendEmail}
                        className="text-sm font-semibold text-blue-700 hover:text-blue-900"
                    >
                        ✉️ Envoyer au client par mail
                    </button>
                )}
            </div>
        </div>
    )
}

function PhotoGallery({ title, photos }: any) {
    return (
        <div className="card">
            <h3 className="font-bold">{title}</h3>
            {photos.length ? (
                <div className="mt-4 grid grid-cols-2 gap-3 md:grid-cols-3">
                    {photos.map((photo: any, index: number) => (
                        <a href={photo.url} target="_blank" rel="noreferrer" key={`${photo.url}-${index}`}>
                            <img src={photo.url} alt={photo.caption || title} className="aspect-[4/3] w-full rounded-lg object-cover shadow-sm" />
                        </a>
                    ))}
                </div>
            ) : (
                <p className="mt-2 text-sm text-slate-500">Aucune photo ajoutée.</p>
            )}
        </div>
    )
}

export default function Show({ project }: any) {
    const survey = project.survey
    const quote = project.quote
    const schedule = project.schedule
    const site = project.site
    const report = project.report
    const photos = project.photos || []
    const expenses = project.expenses || []
    const isManagement = project.isManagement
    const isDg = project.isDg
    const isDt = project.isDt
    const purchaseDone = project.purchases?.some((p: any) => p.status === 'RECEIVED')
    const surveyPhotos = photos.filter((p: any) => p.category === 'SURVEY')
    const closurePhotos = photos.filter((p: any) => p.category === 'CLOSURE')
    const hasFinancialData = isManagement && (project.estimatedBudget || project.budget || project.finalCost || project.profit)

    // Modal pour envoi devis par email
    const [emailModalOpen, setEmailModalOpen] = useState(false)
    const { data: emailData, setData: setEmailData, post: postEmail, processing: emailProcessing } = useForm({
        email: project.clientEmail || '',
    })

    const handleSendEmail = (e: React.FormEvent) => {
        e.preventDefault()
        postEmail(`/projets/${project.id}/devis/envoyer-email/`, {
            onSuccess: () => setEmailModalOpen(false),
        })
    }

    return (
        <AppLayout>
            {/* Header avec N° Projet ETIGE et Référence Client */}
            <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div>
                    <div className="flex flex-wrap items-center gap-2">
                        <span className="rounded-md bg-amber-100 px-2.5 py-1 text-xs font-bold text-amber-800">
                            N° Projet ETIGE : {project.projectNumber}
                        </span>
                        <span className="rounded-md bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
                            Réf Client : {project.reference}
                        </span>
                        {isDg && (
                            <span className="rounded-md bg-purple-100 px-2.5 py-1 text-xs font-semibold text-purple-800">
                                Direction Générale (DG)
                            </span>
                        )}
                        {!isDg && isDt && (
                            <span className="rounded-md bg-blue-100 px-2.5 py-1 text-xs font-semibold text-blue-800">
                                Direction Technique (DT)
                            </span>
                        )}
                    </div>
                    <h2 className="mt-2 text-3xl font-bold text-slate-900">{project.name}</h2>
                    <p className="mt-1 text-slate-600">
                        Client : <strong>{project.client}</strong> {project.clientEmail ? `(${project.clientEmail})` : ''} · {project.address}
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <Status value={project.status} />
                    {isDg && (
                        <Link
                            href={`/projets/${project.id}/modifier/`}
                            className="rounded-lg border border-amber-300 bg-amber-50 px-3 py-2 text-xs font-bold text-amber-800 hover:bg-amber-100"
                        >
                            ✏️ Modifier le projet
                        </Link>
                    )}
                </div>
            </div>

            {/* Modal Envoi Devis par Email */}
            {emailModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4">
                    <div className="card w-full max-w-md bg-white shadow-2xl">
                        <h3 className="text-xl font-bold text-slate-900">Envoyer le devis par email</h3>
                        <p className="mt-1 text-xs text-slate-500">
                            Le devis N° {quote?.number} sera généré en PDF et envoyé en pièce jointe au client.
                        </p>
                        <form onSubmit={handleSendEmail} className="mt-4 space-y-4">
                            <div>
                                <label className="block text-xs font-bold uppercase text-slate-600">Adresse email du client</label>
                                <input
                                    type="email"
                                    required
                                    placeholder="client@entreprise.com"
                                    value={emailData.email}
                                    onChange={(e) => setEmailData('email', e.target.value)}
                                    className="input mt-1"
                                />
                            </div>
                            <div className="flex justify-end gap-3 pt-2">
                                <button
                                    type="button"
                                    onClick={() => setEmailModalOpen(false)}
                                    className="btn-muted text-xs"
                                >
                                    Annuler
                                </button>
                                <button
                                    type="submit"
                                    disabled={emailProcessing}
                                    className="btn-primary text-xs"
                                >
                                    {emailProcessing ? 'Envoi en cours…' : 'Envoyer maintenant'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            <section className="grid gap-5 lg:grid-cols-3">
                {/* Workflow Opérationnel */}
                <div className="card lg:col-span-2">
                    <h3 className="font-bold text-lg text-slate-900">Workflow opérationnel</h3>
                    <p className="mb-5 mt-1 text-sm text-slate-500">
                        Chaque étape suit l'avancement du projet (Survey optionnel, chiffrage, planning, exécution).
                    </p>
                    <div className="grid gap-3">
                        <Step
                            title="1. Survey (Optionnel)"
                            done={!!survey?.validated}
                            href={`/projets/${project.id}/survey/`}
                            text={survey?.validated ? `Visite validée le ${survey.visitDate}` : 'Visite technique et constats terrain (non obligatoire pour faire le devis).'}
                        />
                        <Step
                            title="2. Devis"
                            done={quote?.status === 'APPROVED'}
                            href={`/projets/${project.id}/devis/`}
                            text={quote ? `${quote.number} — ${quote.status === 'APPROVED' ? 'validé' : (quote.status === 'SENT' ? 'envoyé au client' : 'à valider')}` : 'Chiffrage avec gestion des unités (accessible directement).'}
                            quoteExists={!!quote}
                            onSendEmail={() => setEmailModalOpen(true)}
                        />
                        <Step
                            title="3. Planning du projet"
                            done={!!schedule && schedule.tasksCount > 0}
                            href={`/projets/${project.id}/planning/`}
                            text={schedule ? `${schedule.tasksCount} phase(s) définie(s) (${schedule.completedTasksCount} terminée(s))` : 'Définition des phases de travail, dates et jalons après le devis.'}
                            planningExists={!!schedule && schedule.tasksCount > 0}
                            planningPdfHref={`/projets/${project.id}/planning/pdf/`}
                        />
                        <Step
                            title="4. Achats"
                            done={purchaseDone}
                            href={`/projets/${project.id}/achats/`}
                            text={purchaseDone ? 'Au moins une commande réceptionnée.' : 'Commandes fournisseurs après devis validé.'}
                        />
                        <Step
                            title="5. Chantier"
                            done={site?.status === 'COMPLETED'}
                            href={`/projets/${project.id}/chantier/`}
                            text={site ? `${site.progress}% d'avancement` : 'Exécution après réception des achats.'}
                        />
                        <Step
                            title="6. Rapport / clôture"
                            done={!!report}
                            href={`/projets/${project.id}/cloture/`}
                            text={report ? `Livré le ${report.deliveredOn}` : 'Bilan après la fin du chantier.'}
                        />
                    </div>
                </div>

                {/* Sidebar Financière et Dépenses */}
                <aside className="space-y-5">
                    {/* Bilan financier : visible par DG et DT */}
                    {hasFinancialData && (
                        <div className="card">
                            <div className="flex items-center justify-between">
                                <h3 className="font-bold">Bilan Financier</h3>
                                <span className="text-xs text-slate-400 font-medium">Visible DG & DT</span>
                            </div>
                            <dl className="mt-4 space-y-3 text-sm">
                                {project.estimatedBudget && (
                                    <div className="flex justify-between border-b border-dashed border-slate-200 pb-3">
                                        <dt className="italic text-slate-400">Estimation initiale</dt>
                                        <dd className="italic text-slate-400">{Number(project.estimatedBudget).toLocaleString('fr-FR')} FCFA</dd>
                                    </div>
                                )}
                                {project.budget && (
                                    <div className="flex justify-between">
                                        <dt className="font-medium text-slate-500">Budget Final (Client)</dt>
                                        <dd className="font-bold text-amber-700">{Number(project.budget).toLocaleString('fr-FR')} FCFA</dd>
                                    </div>
                                )}
                                {project.finalCost && (
                                    <div className="flex justify-between">
                                        <dt className="text-slate-500">Coût Réel (Achats + Dépenses)</dt>
                                        <dd className="font-bold">{Number(project.finalCost).toLocaleString('fr-FR')} FCFA</dd>
                                    </div>
                                )}
                                {project.profit && (
                                    <div className="flex justify-between border-t border-slate-200 pt-3">
                                        <dt className="font-medium text-slate-500">Bénéfice Réalisé</dt>
                                        <dd className={`font-bold ${Number(project.profit) >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                                            {Number(project.profit).toLocaleString('fr-FR')} FCFA
                                        </dd>
                                    </div>
                                )}
                            </dl>
                        </div>
                    )}

                    {/* Dépenses hors-devis */}
                    <div className="card">
                        <div className="flex items-center justify-between">
                            <h3 className="font-bold">Dépenses hors-devis</h3>
                            <Link href={`/projets/${project.id}/depense/`} className="text-xs font-bold text-amber-700 hover:text-amber-800">+ Ajouter</Link>
                        </div>
                        {expenses.length > 0 ? (
                            <ul className="mt-4 space-y-3">
                                {expenses.map((exp: any, i: number) => (
                                    <li key={i} className="flex justify-between text-sm">
                                        <span className="text-slate-600">{exp.description}</span>
                                        <span className="font-semibold">{Number(exp.amount).toLocaleString('fr-FR')} FCFA</span>
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            <p className="mt-4 text-sm text-slate-500">Aucune dépense enregistrée.</p>
                        )}
                    </div>
                </aside>
            </section>

            {/* Aperçu du Devis avec champ Unité */}
            {quote && quote.lines?.length > 0 && (
                <section className="mt-6 card">
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-3 border-b border-slate-100">
                        <div>
                            <h3 className="font-bold text-lg text-slate-900">Détail du Devis — {quote.number}</h3>
                            <p className="text-xs text-slate-500">Projet {project.projectNumber} · Réf client : {project.reference}</p>
                        </div>
                        <div className="mt-2 sm:mt-0 flex gap-2">
                            <a
                                href={`/projets/${project.id}/devis/pdf/`}
                                target="_blank"
                                rel="noreferrer"
                                className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                            >
                                📄 Télécharger PDF
                            </a>
                            <button
                                type="button"
                                onClick={() => setEmailModalOpen(true)}
                                className="rounded-lg border border-blue-200 bg-blue-50 px-3 py-1.5 text-xs font-semibold text-blue-700 hover:bg-blue-100"
                            >
                                ✉️ Envoyer au client
                            </button>
                        </div>
                    </div>
                    <div className="mt-4 overflow-x-auto">
                        <table className="w-full border-collapse text-left text-sm">
                            <thead>
                                <tr className="border-b border-slate-200 text-xs font-bold uppercase text-slate-500">
                                    <th className="py-2 pr-3">Qté</th>
                                    <th className="py-2 pr-3">Unité</th>
                                    <th className="py-2 pr-3">Désignation</th>
                                    <th className="py-2 pr-3 text-right">Prix Unitaire</th>
                                    <th className="py-2 text-right">Montant</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                                {quote.lines.map((l: any, idx: number) => (
                                    <tr key={idx}>
                                        <td className="py-2.5 pr-3 font-semibold text-slate-900">{l.quantity}</td>
                                        <td className="py-2.5 pr-3 text-slate-600 font-medium">
                                            <span className="rounded bg-slate-100 px-1.5 py-0.5 text-xs">{l.unit || 'u'}</span>
                                        </td>
                                        <td className="py-2.5 pr-3 text-slate-700">{l.designation}</td>
                                        <td className="py-2.5 pr-3 text-right text-slate-600">
                                            {Number(l.unitPrice).toLocaleString('fr-FR')} FCFA
                                        </td>
                                        <td className="py-2.5 text-right font-bold text-slate-900">
                                            {Number(l.amount).toLocaleString('fr-FR')} FCFA
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                            <tfoot>
                                <tr className="border-t-2 border-slate-200 font-bold">
                                    <td colSpan={4} className="py-3 text-right text-slate-700">Total HT :</td>
                                    <td className="py-3 text-right text-amber-700 text-base">
                                        {Number(quote.adjustedAmount || quote.amount).toLocaleString('fr-FR')} FCFA
                                    </td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                </section>
            )}

            <section className="mt-5 grid gap-5 lg:grid-cols-2">
                <PhotoGallery title="Photos du Survey" photos={surveyPhotos} />
                <PhotoGallery title="Photos du résultat final" photos={closurePhotos} />
            </section>
        </AppLayout>
    )
}
