import AppLayout from '../../layouts/AppLayout'
import { Link } from '@inertiajs/react'
import Status from '../../components/Status'

function Step({ title, done, href, text, pdfHref }: any) {
    const downloadHref = pdfHref || (title === '2. Devis' ? href.replace('/devis/', '/devis/pdf/') : null)
    return <div className={`rounded-xl border p-4 ${done ? 'border-emerald-200 bg-emerald-50' : 'border-slate-200 bg-white'}`}><div className="flex items-center justify-between"><div><p className="font-bold">{title}</p><p className="mt-1 text-sm text-slate-500">{text}</p></div><span className={`text-lg ${done ? 'text-emerald-600' : 'text-slate-300'}`}>{done ? '✓' : '○'}</span></div><div className="mt-4 flex flex-wrap gap-4"><Link href={href} className="text-sm font-semibold text-amber-700">{done ? 'Mettre à jour' : 'Renseigner'} →</Link>{downloadHref && done && <a href={downloadHref} className="text-sm font-semibold text-slate-700">Télécharger le PDF</a>}</div></div>
}

function PhotoGallery({ title, photos }: any) {
    return <div className="card"><h3 className="font-bold">{title}</h3>{photos.length ? <div className="mt-4 grid grid-cols-2 gap-3 md:grid-cols-3">{photos.map((photo: any, index: number) => <a href={photo.url} target="_blank" rel="noreferrer" key={`${photo.url}-${index}`}><img src={photo.url} alt={photo.caption || title} className="aspect-[4/3] w-full rounded-lg object-cover" /></a>)}</div> : <p className="mt-2 text-sm text-slate-500">Aucune photo ajoutée.</p>}</div>
}

export default function Show({ project }: any) {
    const survey = project.survey
    const quote = project.quote
    const site = project.site
    const report = project.report
    const photos = project.photos || []
    const purchaseDone = project.purchases?.some((purchase: any) => purchase.status === 'RECEIVED')
    const surveyPhotos = photos.filter((photo: any) => photo.category === 'SURVEY')
    const closurePhotos = photos.filter((photo: any) => photo.category === 'CLOSURE')
    return <AppLayout><div className="mb-8 flex items-start justify-between"><div><Link href="/projets/" className="text-sm font-semibold text-amber-700">← Projets</Link><p className="mt-3 text-xs font-bold text-amber-700">{project.reference}</p><h2 className="text-3xl font-bold">{project.name}</h2><p className="mt-1 text-slate-500">{project.client} · {project.address}</p></div><Status value={project.status} /></div><section className="grid gap-5 lg:grid-cols-3"><div className="card lg:col-span-2"><h3 className="font-bold">Workflow opérationnel</h3><p className="mb-5 mt-1 text-sm text-slate-500">Chaque étape s’ouvre lorsque les prérequis sont remplis.</p><div className="grid gap-3"><Step title="1. Survey" done={!!survey?.validated} href={`/projets/${project.id}/survey/`} text={survey?.validated ? `Visite validée le ${survey.visitDate}` : 'Visite technique et constats.'} /><Step title="2. Devis" done={quote?.status === 'APPROVED'} href={`/projets/${project.id}/devis/`} text={quote ? `${quote.number} — ${quote.status === 'APPROVED' ? 'validé' : 'à valider'}` : 'Chiffrage après validation du Survey.'} /><Step title="3. Achats" done={purchaseDone} href={`/projets/${project.id}/achats/`} text={purchaseDone ? 'Au moins une commande réceptionnée.' : 'Commandes fournisseurs après devis validé.'} /><Step title="4. Chantier" done={site?.status === 'COMPLETED'} href={`/projets/${project.id}/chantier/`} text={site ? `${site.progress}% d’avancement` : 'Exécution après réception des achats.'} /><Step title="5. Rapport / clôture" done={!!report} href={`/projets/${project.id}/cloture/`} text={report ? `Livré le ${report.deliveredOn}` : 'Bilan après la fin du chantier.'} /></div></div><aside className="space-y-5"><div className="card"><h3 className="font-bold">Indicateurs</h3><dl className="mt-4 space-y-3 text-sm"><div className="flex justify-between"><dt className="text-slate-500">Estimation du budget</dt><dd className="font-bold">{Number(project.budget).toLocaleString('fr-FR')} FCFA</dd></div><div className="flex justify-between"><dt className="text-slate-500">Référence</dt><dd className="font-bold">{project.reference}</dd></div></dl></div></aside></section><section className="mt-5 grid gap-5 lg:grid-cols-2"><PhotoGallery title="Photos du Survey" photos={surveyPhotos} /><PhotoGallery title="Photos du résultat final" photos={closurePhotos} /></section></AppLayout>
}
