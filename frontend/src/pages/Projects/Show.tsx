import AppLayout from '../../layouts/AppLayout'
import { Link, useForm } from '@inertiajs/react'
import Status from '../../components/Status'
import { useState } from 'react'

function Step({ title, done, href, text, pdfHref, onSendEmail, quoteExists, planningExists, planningPdfHref, actionText }: any) {
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
                    {actionText || (done ? 'Mettre à jour' : 'Renseigner')} →
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
                        ✉️ Envoyer au client
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
    const quotes = project.quotes || []
    const purchases = project.purchases || []
    const documents = project.documents || []
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
    const [fileModalOpen, setFileModalOpen] = useState(false)
    const { data: fileData, setData: setFileData, post: postFile, processing: fileProcessing } = useForm({
        name: '',
        category: 'OTHER',
        file: null as any
    })
    
    const handleFileUpload = (e: React.FormEvent) => {
        e.preventDefault()
        postFile(`/projets/${project.id}/documents/`, {
            forceFormData: true,
            onSuccess: () => {
                setFileModalOpen(false)
                setFileData('name', '')
                setFileData('file', null)
            }
        })
    }

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

            {/* Modal Upload Fichier */}
            {fileModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4">
                    <div className="card w-full max-w-md bg-white shadow-2xl">
                        <h3 className="text-xl font-bold text-slate-900">Ajouter un document</h3>
                        <form onSubmit={handleFileUpload} className="mt-4 space-y-4" encType="multipart/form-data">
                            <div>
                                <label className="block text-xs font-bold uppercase text-slate-600">Catégorie</label>
                                <select required value={fileData.category} onChange={(e) => setFileData('category', e.target.value)} className="input mt-1">
                                    <option value="QUOTE">Devis signé</option>
                                    <option value="INVOICE">Facture</option>
                                    <option value="DELIVERY_SLIP">Bon de livraison</option>
                                    <option value="PHOTO">Photo</option>
                                    <option value="OTHER">Autre</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-xs font-bold uppercase text-slate-600">Nom du document</label>
                                <input type="text" required value={fileData.name} onChange={(e) => setFileData('name', e.target.value)} className="input mt-1" />
                            </div>
                            <div>
                                <label className="block text-xs font-bold uppercase text-slate-600">Fichier</label>
                                <input type="file" required onChange={(e) => setFileData('file', e.target.files?.[0])} className="input mt-1" />
                            </div>
                            <div className="flex justify-end gap-3 pt-2">
                                <button type="button" onClick={() => setFileModalOpen(false)} className="btn-muted text-xs">Annuler</button>
                                <button type="submit" disabled={fileProcessing} className="btn-primary text-xs">{fileProcessing ? 'Envoi...' : 'Ajouter'}</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
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
                            done={quote?.status === 'ACCEPTED'}
                            href={`/projets/${project.id}/devis/`}
                            text={quote ? `Devis Accepté : ${quote.number}` : 'Chiffrage avec gestion des unités (accessible directement).'}
                            quoteExists={!!quote}
                            onSendEmail={quote ? () => setEmailModalOpen(true) : undefined}
                            actionText="Gérer les devis"
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
                            actionText="Nouvel achat"
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

            {/* Historique des Devis */}
            <section className="mt-6 card">
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <h3 className="font-bold text-lg text-slate-900">Historique des Devis</h3>
                </div>
                {quotes.length > 0 ? (
                    <div className="mt-4 overflow-x-auto">
                        <table className="w-full border-collapse text-left text-sm">
                            <thead>
                                <tr className="border-b border-slate-200 text-xs font-bold uppercase text-slate-500">
                                    <th className="py-2 pr-3">Numéro</th>
                                    <th className="py-2 pr-3 text-right">Montant HT</th>
                                    <th className="py-2 pr-3">Statut</th>
                                    <th className="py-2 text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                                {quotes.map((q: any) => (
                                    <tr key={q.id}>
                                        <td className="py-2.5 font-bold text-slate-900">{q.number}</td>
                                        <td className="py-2.5 text-right font-semibold">{Number(q.amount).toLocaleString('fr-FR')} FCFA</td>
                                        <td className="py-2.5"><Status value={q.status} /></td>
                                        <td className="py-2.5 text-right text-xs space-x-2">
                                            <a href={`/projets/${project.id}/devis/pdf/?quote_id=${q.id}`} target="_blank" rel="noreferrer" className="text-slate-600 hover:text-slate-900 font-bold">PDF</a>
                                            <Link href={`/projets/${project.id}/devis/${q.id}/`} className="text-amber-700 hover:text-amber-900 font-bold">Modifier</Link>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <p className="mt-4 text-sm text-slate-500">Aucun devis enregistré.</p>
                )}
            </section>

            {/* Historique des Achats */}
            <section className="mt-6 card">
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <h3 className="font-bold text-lg text-slate-900">Suivi des Achats</h3>
                </div>
                {purchases.length > 0 ? (
                    <div className="mt-4 space-y-4">
                        {purchases.map((p: any) => (
                            <div key={p.id} className="border border-slate-200 rounded-lg p-4">
                                <div className="flex justify-between items-center border-b border-slate-100 pb-2 mb-2">
                                    <div>
                                        <span className="font-bold text-slate-900 mr-3">{p.reference}</span>
                                        <span className="text-slate-500">{p.supplier}</span>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <span className="font-bold text-lg">{Number(p.amount).toLocaleString('fr-FR')} FCFA</span>
                                        <Status value={p.status} />
                                        <Link href={`/projets/${project.id}/achats/${p.id}/`} className="text-xs font-bold text-amber-700 hover:text-amber-900">Modifier</Link>
                                    </div>
                                </div>
                                <div className="text-xs text-slate-500 space-y-1">
                                    {p.lines?.map((l: any, idx: number) => (
                                        <div key={idx} className="flex justify-between">
                                            <span>{l.quantity} {l.unit} - {l.designation}</span>
                                            <span>{Number(l.amount).toLocaleString('fr-FR')} FCFA</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="mt-4 text-sm text-slate-500">Aucun achat enregistré.</p>
                )}
            </section>
            
            {/* Documents et Fichiers */}
            <section className="mt-6 card">
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <h3 className="font-bold text-lg text-slate-900">Documents et Fichiers</h3>
                    <button onClick={() => setFileModalOpen(true)} className="btn-muted text-xs">
                        + Ajouter un document
                    </button>
                </div>
                {documents.length > 0 ? (
                    <div className="mt-4 grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                        {documents.map((doc: any) => (
                            <div key={doc.id} className="flex items-center justify-between p-3 border border-slate-200 rounded-lg">
                                <div className="overflow-hidden">
                                    <p className="font-bold text-sm truncate" title={doc.name}>{doc.name}</p>
                                    <p className="text-xs text-slate-500">{doc.category}</p>
                                </div>
                                <div className="flex gap-2">
                                    <a href={doc.url} target="_blank" rel="noreferrer" className="text-blue-600 hover:text-blue-800 text-sm font-bold">Ouvrir</a>
                                    {isDg && (
                                        <Link method="post" href={`/projets/documents/${doc.id}/supprimer/`} as="button" className="text-red-600 hover:text-red-800 text-sm font-bold" preserveScroll>✖</Link>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="mt-4 text-sm text-slate-500">Aucun document joint.</p>
                )}
            </section>


            <section className="mt-5 grid gap-5 lg:grid-cols-2">
                <PhotoGallery title="Photos du Survey" photos={surveyPhotos} />
                <PhotoGallery title="Photos du résultat final" photos={closurePhotos} />
            </section>
        </AppLayout>
    )
}
