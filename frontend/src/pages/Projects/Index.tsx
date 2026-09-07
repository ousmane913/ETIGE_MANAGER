import AppLayout from '../../layouts/AppLayout'
import { Link, useForm, router } from '@inertiajs/react'
import Status from '../../components/Status'
import { useState } from 'react'

function ProjectCard({ project, isDg }: any) {
    const { post, processing } = useForm({})
    const deleteProject = (event: React.FormEvent) => {
        event.preventDefault()
        if (window.confirm(`Souhaitez-vous supprimer le projet « ${project.name} » ?`)) {
            post(`/projets/${project.id}/supprimer/`)
        }
    }

    return (
        <div className="card transition hover:-translate-y-0.5 hover:shadow-md">
            <Link href={`/projets/${project.id}/`} className="block">
                <div className="flex justify-between gap-3">
                    <div>
                        <div className="flex flex-wrap items-center gap-2">
                            <span className="rounded bg-amber-100 px-2 py-0.5 text-xs font-bold text-amber-800">
                                {project.project_number || 'N° non défini'}
                            </span>
                            <span className="text-xs text-slate-500">
                                Réf: <strong className="text-slate-700">{project.reference}</strong>
                            </span>
                        </div>
                        <h3 className="mt-2 text-lg font-bold text-slate-900">{project.name}</h3>
                        <p className="mt-1 text-sm text-slate-600 font-medium">Client : {project.client}</p>
                    </div>
                    <Status value={project.status} />
                </div>
                <div className="mt-4 flex flex-wrap items-center justify-between border-t border-slate-100 pt-3 text-xs text-slate-500">
                    <span>Échéance : {project.target_end_date ? new Date(project.target_end_date).toLocaleDateString('fr-FR') : 'Non définie'}</span>
                    <span className="font-semibold text-slate-700">
                        {Number(project.budget) > 0 ? `${Number(project.budget).toLocaleString('fr-FR')} FCFA` : 'Budget non défini'}
                    </span>
                </div>
            </Link>
            {isDg && (
                <div className="mt-4 flex justify-end gap-2 border-t border-slate-100 pt-3">
                    <Link
                        href={`/projets/${project.id}/modifier/`}
                        className="rounded-lg border border-amber-200 px-3 py-1.5 text-xs font-semibold text-amber-700 hover:bg-amber-50"
                    >
                        Modifier
                    </Link>
                    <form onSubmit={deleteProject}>
                        <button
                            type="submit"
                            disabled={processing}
                            className="rounded-lg border border-red-200 px-3 py-1.5 text-xs font-semibold text-red-700 hover:bg-red-50 disabled:opacity-50"
                        >
                            {processing ? 'Suppression…' : 'Supprimer'}
                        </button>
                    </form>
                </div>
            )}
        </div>
    )
}

export default function Projects({ projects, searchQuery, isDg }: any) {
    const [search, setSearch] = useState(searchQuery || '')

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault()
        router.get('/projets/', { q: search }, { preserveState: true })
    }

    return (
        <AppLayout>
            <div className="mb-7 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <h2 className="text-3xl font-bold">Projets</h2>
                    <p className="text-slate-500">Suivez chaque projet ETIGE avec son numéro de projet et sa référence client.</p>
                </div>
                <Link href="/projets/nouveau/" className="btn-primary">
                    + Nouveau projet
                </Link>
            </div>

            {/* Barre de recherche par N° projet, Référence, Client ou Nom */}
            <form onSubmit={handleSearch} className="mb-6 flex gap-2">
                <input
                    type="search"
                    placeholder="Rechercher par N° projet ETIGE, Réf client, Client ou Nom…"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="input mt-0 max-w-lg bg-white"
                />
                <button type="submit" className="btn-primary py-2 text-sm">
                    Rechercher
                </button>
                {search && (
                    <button
                        type="button"
                        onClick={() => { setSearch(''); router.get('/projets/') }}
                        className="btn-muted py-2 text-sm"
                    >
                        Réinitialiser
                    </button>
                )}
            </form>

            <div className="grid gap-4 md:grid-cols-2">
                {projects.map((project: any) => (
                    <ProjectCard key={project.id} project={project} isDg={isDg} />
                ))}
                {!projects.length && (
                    <div className="card col-span-2 text-center text-slate-500">
                        {search ? `Aucun projet ne correspond à la recherche « ${search} ».` : 'Créez votre premier projet pour démarrer le workflow.'}
                    </div>
                )}
            </div>
        </AppLayout>
    )
}
