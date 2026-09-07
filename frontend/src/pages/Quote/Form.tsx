import AppLayout from '../../layouts/AppLayout'
import { useForm } from '@inertiajs/react'

function amount(line: any, isManagement: boolean) {
    if (isManagement && line.adjustedUnitPrice) {
        return Number(line.quantity || 0) * Number(line.adjustedUnitPrice);
    }
    return Number(line.quantity || 0) * Number(line.unitPrice || 0)
}

const COMMON_UNITS = [
    'u', 'm', 'cm', 'm²', 'm³', 'ens', 'kg', 'tonne', 'forfait', 'j', 'h', 'litre'
]

export default function QuoteForm({ title, subtitle, action, fields, errors, lines: initialLines, is_management, project }: any) {
    const initialFields = Object.fromEntries(fields.map((field: any) => [field.name, field.initial ?? '']))
    const normalizedInitialLines = initialLines?.length
        ? initialLines.map((l: any) => ({ ...l, unit: l.unit || 'u' }))
        : [{ quantity: '1', unit: 'u', designation: '', unitPrice: '', adjustedUnitPrice: '' }]

    const { data, setData, post, processing } = useForm({
        ...initialFields,
        lines: normalizedInitialLines
    })

    const total = data.lines.reduce((sum: number, line: any) => sum + amount(line, is_management), 0)
    const updateLine = (index: number, key: string, value: string) =>
        setData('lines', data.lines.map((line: any, lineIndex: number) => (lineIndex === index ? { ...line, [key]: value } : line)))
    const addLine = () =>
        setData('lines', [...data.lines, { quantity: '1', unit: 'u', designation: '', unitPrice: '', adjustedUnitPrice: '' }])
    const removeLine = (index: number) =>
        setData('lines', data.lines.filter((_: any, lineIndex: number) => lineIndex !== index))

    const submit = (event: React.FormEvent) => {
        event.preventDefault()
        post(action, { transform: (formData) => ({ ...formData, lines: JSON.stringify(formData.lines) }) })
    }

    return (
        <AppLayout>
            <div className="mx-auto max-w-5xl">
                <div className="mb-6">
                    <div className="flex flex-wrap items-center gap-2">
                        {project && (
                            <>
                                <span className="rounded bg-amber-100 px-2.5 py-1 text-xs font-bold text-amber-800">
                                    N° Projet ETIGE : {project.projectNumber}
                                </span>
                                <span className="rounded bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
                                    Réf Client : {project.reference}
                                </span>
                                <span className="rounded bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
                                    Client : {project.client}
                                </span>
                            </>
                        )}
                    </div>
                    <h2 className="mt-2 text-3xl font-bold">{title}</h2>
                    <p className="mt-1 text-slate-500">{subtitle}</p>
                </div>

                <form className="card" onSubmit={submit}>
                    {errors?.__all__ && (
                        <div className="mb-5 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-700" role="alert">
                            {errors.__all__.map((error: string) => (
                                <p key={error}>{error}</p>
                            ))}
                        </div>
                    )}

                    <div className="grid gap-5 md:grid-cols-3">
                        <label className="text-sm font-semibold">
                            Numéro de devis
                            <input
                                className="input"
                                value={data.number}
                                onChange={(e) => setData('number', e.target.value)}
                                required
                            />
                        </label>
                        <label className="text-sm font-semibold">
                            Date de validité
                            <input
                                className="input"
                                type="date"
                                value={data.validity_date}
                                onChange={(e) => setData('validity_date', e.target.value)}
                            />
                        </label>
                        <label className="text-sm font-semibold">
                            Statut
                            <select
                                className="input"
                                value={data.status}
                                onChange={(e) => setData('status', e.target.value)}
                                required
                            >
                                {fields
                                    .find((field: any) => field.name === 'status')
                                    ?.choices?.map((choice: any) => (
                                        <option key={choice[0]} value={choice[0]}>
                                            {choice[1]}
                                        </option>
                                    ))}
                            </select>
                        </label>
                    </div>

                    <div className="mt-8 overflow-x-auto">
                        <datalist id="common-units">
                            {COMMON_UNITS.map((u) => (
                                <option key={u} value={u} />
                            ))}
                        </datalist>

                        <table className="w-full min-w-[760px] border-collapse text-sm">
                            <thead>
                                <tr className="border-b border-slate-200 text-left text-slate-500">
                                    <th className="p-3 w-24">Quantité</th>
                                    <th className="p-3 w-28">Unité</th>
                                    <th className="p-3">Désignation</th>
                                    <th className="p-3 w-36">Prix unitaire (Tech)</th>
                                    {is_management && <th className="p-3 w-36 text-amber-700">Prix unitaire (Client)</th>}
                                    <th className="p-3 text-right w-36">Montant</th>
                                    <th className="p-3 w-16"></th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.lines.map((line: any, index: number) => (
                                    <tr className="border-b border-slate-100" key={index}>
                                        <td className="p-2">
                                            <input
                                                className="input mt-0 w-full"
                                                type="number"
                                                min="1"
                                                step="1"
                                                value={line.quantity}
                                                onChange={(e) => updateLine(index, 'quantity', e.target.value)}
                                                required
                                            />
                                        </td>
                                        <td className="p-2">
                                            <input
                                                className="input mt-0 w-full"
                                                type="text"
                                                list="common-units"
                                                placeholder="ex: m, m3, ens"
                                                value={line.unit}
                                                onChange={(e) => updateLine(index, 'unit', e.target.value)}
                                                required
                                            />
                                        </td>
                                        <td className="p-2">
                                            <input
                                                className="input mt-0 w-full"
                                                value={line.designation}
                                                onChange={(e) => updateLine(index, 'designation', e.target.value)}
                                                placeholder="Désignation de la ligne"
                                                required
                                            />
                                        </td>
                                        <td className="p-2">
                                            <input
                                                className="input mt-0 w-full"
                                                type="number"
                                                min="0.01"
                                                step="0.01"
                                                value={line.unitPrice}
                                                onChange={(e) => updateLine(index, 'unitPrice', e.target.value)}
                                                required
                                            />
                                        </td>
                                        {is_management && (
                                            <td className="p-2">
                                                <input
                                                    className="input mt-0 w-full border-amber-300 focus:border-amber-500"
                                                    type="number"
                                                    min="0.01"
                                                    step="0.01"
                                                    value={line.adjustedUnitPrice || ''}
                                                    onChange={(e) => updateLine(index, 'adjustedUnitPrice', e.target.value)}
                                                    placeholder="Lui-même par défaut"
                                                />
                                            </td>
                                        )}
                                        <td className="p-3 text-right font-semibold whitespace-nowrap">
                                            {amount(line, is_management).toLocaleString('fr-FR')} FCFA
                                        </td>
                                        <td className="p-2 text-right">
                                            <button
                                                type="button"
                                                onClick={() => removeLine(index)}
                                                disabled={data.lines.length === 1}
                                                className="text-sm font-semibold text-red-700 disabled:opacity-30 hover:underline"
                                            >
                                                ✕
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>

                        <button type="button" onClick={addLine} className="btn-muted mt-4">
                            + Ajouter une ligne
                        </button>
                    </div>

                    <label className="mt-7 block text-sm font-semibold">
                        Notes
                        <textarea
                            className="input"
                            rows={4}
                            value={data.notes}
                            onChange={(e) => setData('notes', e.target.value)}
                            placeholder="Modalités de paiement, validité, conditions techniques…"
                        />
                    </label>

                    <div className="mt-7 flex flex-col sm:flex-row items-end sm:items-center justify-between border-t border-slate-200 pt-5">
                        <span className="text-xs text-slate-500">
                            * Les unités supportées incluent mètre (m), centimètre (cm), m², m³, ensemble (ens), unité (u), etc.
                        </span>
                        <div className="text-right mt-4 sm:mt-0">
                            <p className="text-sm text-slate-500">Montant total HT</p>
                            <p className="text-2xl font-bold text-slate-900">{total.toLocaleString('fr-FR')} FCFA</p>
                            <button disabled={processing} className="btn-primary mt-3">
                                {processing ? 'Enregistrement…' : 'Enregistrer le devis'}
                            </button>
                        </div>
                    </div>
                </form>
            </div>
        </AppLayout>
    )
}
