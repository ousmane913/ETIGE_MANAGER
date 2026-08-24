import AppLayout from '../../layouts/AppLayout'
import { Link, useForm } from '@inertiajs/react'
import Status from '../../components/Status'
function ProjectCard({ project }: any) {
	const { post, processing } = useForm({})
	const deleteProject = (event: React.FormEvent) => {
		event.preventDefault()
		if (window.confirm(`Souhaitez-vous supprimer le projet « ${project.name} » ?`)) post(`/projets/${project.id}/supprimer/`)
	}
	return <div className="card transition hover:-translate-y-0.5 hover:shadow-md"><Link href={`/projets/${project.id}/`} className="block"><div className="flex justify-between gap-3"><div><p className="text-xs font-bold text-amber-700">{project.reference}</p><h3 className="mt-1 text-lg font-bold">{project.name}</h3><p className="mt-1 text-sm text-slate-500">{project.client}</p></div><Status value={project.status} /></div><p className="mt-5 text-sm text-slate-500">Estimation du budget : <span className="font-semibold text-slate-700">{Number(project.budget).toLocaleString('fr-FR')} FCFA</span></p></Link><div className="mt-4 flex justify-end gap-2"><Link href={`/projets/${project.id}/modifier/`} className="rounded-lg border border-amber-200 px-3 py-2 text-sm font-semibold text-amber-700 hover:bg-amber-50">Modifier</Link><form onSubmit={deleteProject}><button type="submit" disabled={processing} className="rounded-lg border border-red-200 px-3 py-2 text-sm font-semibold text-red-700 hover:bg-red-50 disabled:opacity-50">{processing ? 'Suppression…' : 'Supprimer'}</button></form></div></div>
}

export default function Projects({ projects }: any) { return <AppLayout><div className="mb-7 flex items-center justify-between"><div><h2 className="text-3xl font-bold">Projets</h2><p className="text-slate-500">Suivez chaque projet de l’étude à la clôture.</p></div><Link href="/projets/nouveau/" className="btn-primary">+ Nouveau projet</Link></div><div className="grid gap-4 md:grid-cols-2">{projects.map((project: any) => <ProjectCard key={project.id} project={project} />)}{!projects.length && <div className="card text-slate-500">Créez votre premier projet pour démarrer le workflow.</div>}</div></AppLayout> }
