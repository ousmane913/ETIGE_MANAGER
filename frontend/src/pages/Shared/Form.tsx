import AppLayout from '../../layouts/AppLayout'
import { useForm } from '@inertiajs/react'
import { useEffect } from 'react'

function statusForProgress(progress: unknown) {
    const value = Number(progress)
    if (value === 0) return 'NOT_STARTED'
    if (value === 100) return 'COMPLETED'
    return value > 0 && value < 100 ? 'IN_PROGRESS' : ''
}

function normalizeProgress(progress: unknown) {
    const value = Number(progress)
    if (!Number.isFinite(value)) return ''
    return Math.min(100, Math.max(0, value))
}

export default function FormPage({ title, subtitle, action, fields, errors }: any) {
    const initial = Object.fromEntries(fields.map((field: any) => [field.name, field.type === 'checkbox' ? field.initial === 'True' : (field.type === 'file' ? null : (field.initial ?? ''))]))
    const isSiteForm = fields.some((field: any) => field.name === 'progress') && fields.some((field: any) => field.name === 'status')
    const hasFiles = fields.some((field: any) => field.type === 'file')
    const { data, setData, post, processing } = useForm(initial)
    useEffect(() => {
        if (isSiteForm) {
            const progress = normalizeProgress(data.progress)
            if (progress !== data.progress) setData('progress', progress)
            setData('status', statusForProgress(progress))
        }
    }, [data.progress, isSiteForm, setData])

    return <AppLayout><div className="mx-auto max-w-2xl"><h2 className="text-3xl font-bold">{title}</h2><p className="mb-7 mt-1 text-slate-500">{subtitle}</p><form className="card" encType={hasFiles ? 'multipart/form-data' : undefined} onSubmit={event => { event.preventDefault(); post(action, { forceFormData: hasFiles }) }}>{errors?.__all__ && <div className="mb-5 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-700" role="alert">{errors.__all__.map((error: string) => <p key={error}>{error}</p>)}</div>}<div className="grid gap-5 md:grid-cols-2">{fields.map((field: any) => <label key={field.name} className={`text-sm font-semibold ${['address','findings','technical_notes','notes','description','summary','lessons_learned'].includes(field.name) || field.type === 'file' ? 'md:col-span-2' : ''}`}>{field.label}{field.type === 'file' ? <input className="input" type="file" accept="image/*" multiple onChange={event => setData(field.name, Array.from(event.target.files || []))} /> : field.type === 'checkbox' ? <input className="ml-3" type="checkbox" checked={data[field.name]} onChange={event => setData(field.name, event.target.checked)} /> : field.choices ? <select required={field.required} disabled={isSiteForm && field.name === 'status'} className="input disabled:cursor-not-allowed disabled:bg-slate-100" value={data[field.name]} onChange={event => setData(field.name, event.target.value)}><option value="">Sélectionner…</option>{field.choices.map((choice: any) => <option key={choice[0]} value={choice[0]}>{choice[1]}</option>)}</select> : field.type === 'textarea' ? <textarea required={field.required} className="input" rows={4} value={data[field.name]} onChange={event => setData(field.name, event.target.value)} /> : <input required={field.required} type={field.type || 'text'} className="input" value={data[field.name]} onChange={event => setData(field.name, event.target.value)} />}{errors?.[field.name] && <span className="mt-1 block text-xs font-normal text-red-600">{errors[field.name][0]}</span>}</label>)}</div><div className="mt-7 flex justify-end"><button disabled={processing} className="btn-primary">{processing ? 'Enregistrement…' : 'Enregistrer'}</button></div></form></div></AppLayout>
}
