import AppLayout from '../../layouts/AppLayout'
import { useForm, Link } from '@inertiajs/react'

export default function Planning({ project, schedule, tasks: initialTasks, statusChoices }: any) {
    const { data, setData, post, processing } = useForm({
        start_date: schedule?.startDate || '',
        end_date: schedule?.endDate || '',
        notes: schedule?.notes || '',
        tasks: initialTasks?.length
            ? initialTasks
            : [{ name: '', description: '', startDate: '', endDate: '', assignedTo: '', status: 'TODO' }]
    })

    const updateTask = (index: number, key: string, value: string) => {
        setData('tasks', data.tasks.map((task: any, idx: number) =>
            idx === index ? { ...task, [key]: value } : task
        ))
    }

    const addTask = () => {
        setData('tasks', [
            ...data.tasks,
            { name: '', description: '', startDate: '', endDate: '', assignedTo: '', status: 'TODO' }
        ])
    }

    const removeTask = (index: number) => {
        setData('tasks', data.tasks.filter((_: any, idx: number) => idx !== index))
    }

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        post(`/projets/${project.id}/planning/`, {
            transform: (formData) => ({
                ...formData,
                tasks: JSON.stringify(formData.tasks)
            })
        })
    }

    // Calcul de durée en jours pour l'affichage en direct
    const calculateDays = (start: string, end: string) => {
        if (!start || !end) return null
        const d1 = new Date(start)
        const d2 = new Date(end)
        const diffTime = d2.getTime() - d1.getTime()
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
        return diffDays > 0 ? diffDays : 0
    }

    const globalDuration = calculateDays(data.start_date, data.end_date)

    return (
        <AppLayout>
            <div className="mx-auto max-w-5xl">
                <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                        <div className="flex flex-wrap items-center gap-2">
                            <span className="rounded bg-amber-100 px-2.5 py-1 text-xs font-bold text-amber-800">
                                N° Projet ETIGE : {project.projectNumber}
                            </span>
                            <span className="rounded bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
                                Réf Client : {project.reference}
                            </span>
                            <span className="rounded bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
                                Client : {project.client}
                            </span>
                        </div>
                        <h2 className="mt-2 text-3xl font-bold text-slate-900">Planning & Déroulement du projet</h2>
                        <p className="mt-1 text-sm text-slate-500">
                            Établissez le calendrier officiel, les phases de réalisation et le déroulement complet des opérations.
                        </p>
                    </div>
                    <div className="flex items-center gap-2">
                        {initialTasks?.length > 0 && (
                            <a
                                href={`/projets/${project.id}/planning/pdf/`}
                                target="_blank"
                                rel="noreferrer"
                                className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-bold text-slate-700 shadow-sm hover:bg-slate-50"
                            >
                                📄 Télécharger PDF (Client)
                            </a>
                        )}
                        <Link href={`/projets/${project.id}/`} className="btn-muted text-xs">
                            ← Fiche projet
                        </Link>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Cadre dates globales & déroulement global */}
                    <div className="card">
                        <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
                            <h3 className="font-bold text-lg text-slate-900">
                                1. Période globale d'exécution
                            </h3>
                            {globalDuration !== null && (
                                <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-bold text-emerald-800">
                                    Durée estimée : {globalDuration} jour{globalDuration > 1 ? 's' : ''}
                                </span>
                            )}
                        </div>
                        <div className="grid gap-5 sm:grid-cols-2">
                            <label className="text-sm font-semibold">
                                Date de début prévisionnelle
                                <input
                                    type="date"
                                    className="input"
                                    value={data.start_date}
                                    onChange={(e) => setData('start_date', e.target.value)}
                                />
                            </label>
                            <label className="text-sm font-semibold">
                                Date de fin prévisionnelle
                                <input
                                    type="date"
                                    className="input"
                                    value={data.end_date}
                                    onChange={(e) => setData('end_date', e.target.value)}
                                />
                            </label>
                        </div>
                        <label className="mt-4 block text-sm font-semibold">
                            Notes générales sur le déroulement (exigences client, accès chantier, livrables…)
                            <textarea
                                className="input"
                                rows={3}
                                value={data.notes}
                                onChange={(e) => setData('notes', e.target.value)}
                                placeholder="Précisez ici les conditions de déroulement, contraintes matérielles ou délais impératifs pour le client…"
                            />
                        </label>
                    </div>

                    {/* Découpage en phases */}
                    <div className="card">
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-slate-100 pb-3 mb-4">
                            <div>
                                <h3 className="font-bold text-lg text-slate-900">
                                    2. Découpage en phases & déroulement des opérations
                                </h3>
                                <p className="text-xs text-slate-500">
                                    Détaillez chaque étape pour que le client comprenne précisément la chronologie et les actions menées.
                                </p>
                            </div>
                            <button
                                type="button"
                                onClick={addTask}
                                className="btn-primary text-xs mt-3 sm:mt-0"
                            >
                                + Ajouter une phase
                            </button>
                        </div>

                        <div className="space-y-4">
                            {data.tasks.map((task: any, index: number) => {
                                const days = calculateDays(task.startDate, task.endDate)
                                return (
                                    <div key={index} className="rounded-xl border border-slate-200 bg-slate-50/50 p-4 transition hover:border-slate-300">
                                        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                                            <span className="font-bold text-sm text-amber-800">
                                                Phase {index + 1}
                                            </span>
                                            <div className="flex items-center gap-3">
                                                {days !== null && (
                                                    <span className="text-xs font-semibold text-slate-600 bg-white border border-slate-200 px-2 py-0.5 rounded">
                                                        ⏱️ {days} jour{days > 1 ? 's' : ''}
                                                    </span>
                                                )}
                                                <button
                                                    type="button"
                                                    onClick={() => removeTask(index)}
                                                    disabled={data.tasks.length === 1}
                                                    className="text-xs font-semibold text-red-600 hover:text-red-800 disabled:opacity-30"
                                                >
                                                    Supprimer
                                                </button>
                                            </div>
                                        </div>

                                        <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                                            <div className="sm:col-span-2">
                                                <label className="text-xs font-bold uppercase text-slate-600">Nom de la phase / Étape</label>
                                                <input
                                                    className="input mt-1 bg-white"
                                                    placeholder="ex: Phase 1 : Installation et approvisionnement"
                                                    value={task.name}
                                                    onChange={(e) => updateTask(index, 'name', e.target.value)}
                                                    required
                                                />
                                            </div>
                                            <div>
                                                <label className="text-xs font-bold uppercase text-slate-600">Date de début</label>
                                                <input
                                                    type="date"
                                                    className="input mt-1 bg-white"
                                                    value={task.startDate}
                                                    onChange={(e) => updateTask(index, 'startDate', e.target.value)}
                                                />
                                            </div>
                                            <div>
                                                <label className="text-xs font-bold uppercase text-slate-600">Date de fin</label>
                                                <input
                                                    type="date"
                                                    className="input mt-1 bg-white"
                                                    value={task.endDate}
                                                    onChange={(e) => updateTask(index, 'endDate', e.target.value)}
                                                />
                                            </div>
                                        </div>

                                        <div className="mt-3 grid gap-3 sm:grid-cols-3">
                                            <div className="sm:col-span-2">
                                                <label className="text-xs font-bold uppercase text-slate-600">
                                                    Déroulement des opérations & actions prévues (destiné au client)
                                                </label>
                                                <textarea
                                                    className="input mt-1 bg-white"
                                                    rows={2}
                                                    placeholder="Détaillez les travaux exécutés, méthodologie, équipements mobilisés, livrables attendus…"
                                                    value={task.description || ''}
                                                    onChange={(e) => updateTask(index, 'description', e.target.value)}
                                                />
                                            </div>
                                            <div>
                                                <label className="text-xs font-bold uppercase text-slate-600">Responsable / Équipe</label>
                                                <input
                                                    className="input mt-1 bg-white"
                                                    placeholder="ex: Chef de chantier"
                                                    value={task.assignedTo}
                                                    onChange={(e) => updateTask(index, 'assignedTo', e.target.value)}
                                                />
                                                <label className="mt-2 block text-xs font-bold uppercase text-slate-600">Statut</label>
                                                <select
                                                    className="input mt-1 bg-white"
                                                    value={task.status}
                                                    onChange={(e) => updateTask(index, 'status', e.target.value)}
                                                >
                                                    {statusChoices?.map((choice: any) => (
                                                        <option key={choice[0]} value={choice[0]}>
                                                            {choice[1]}
                                                        </option>
                                                    )) || (
                                                        <>
                                                            <option value="TODO">À faire</option>
                                                            <option value="IN_PROGRESS">En cours</option>
                                                            <option value="DONE">Terminé</option>
                                                        </>
                                                    )}
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                )
                            })}
                        </div>
                    </div>

                    <div className="flex justify-end gap-3 pt-2">
                        <Link href={`/projets/${project.id}/`} className="btn-muted">
                            Annuler
                        </Link>
                        <button type="submit" disabled={processing} className="btn-primary">
                            {processing ? 'Enregistrement…' : 'Enregistrer le planning'}
                        </button>
                    </div>
                </form>
            </div>
        </AppLayout>
    )
}
