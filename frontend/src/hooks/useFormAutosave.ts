import { useEffect, useRef, useState } from 'react'

function csrfToken() {
    return document.cookie.match(/(?:^|; )csrftoken=([^;]+)/)?.[1] || ''
}

export function useFormAutosave(key: string, data: any, setData: any, enabled = true, excludedKeys: string[] = []) {
    const [loaded, setLoaded] = useState(false)
    const [status, setStatus] = useState('')
    const dataRef = useRef(data)
    const baselineRef = useRef(JSON.stringify(data))
    const excludedRef = useRef(excludedKeys)
    const timeoutRef = useRef<number | null>(null)
    const pendingSaveRef = useRef<Promise<Response> | null>(null)

    useEffect(() => {
        dataRef.current = data
    }, [data])

    useEffect(() => {
        excludedRef.current = excludedKeys
    }, [excludedKeys])

    useEffect(() => {
        if (!enabled) {
            setLoaded(true)
            return
        }

        let active = true
        setLoaded(false)
        baselineRef.current = JSON.stringify(dataRef.current)
        fetch(`/form-drafts/?key=${encodeURIComponent(key)}`, { credentials: 'same-origin' })
            .then((response) => response.ok ? response.json() : Promise.reject())
            .then((result) => {
                if (!active) return
                if (result.data && JSON.stringify(dataRef.current) === baselineRef.current) {
                    setData({ ...dataRef.current, ...result.data })
                    setStatus('Brouillon récupéré')
                }
            })
            .catch(() => {
                if (active) setStatus('')
            })
            .finally(() => {
                if (active) setLoaded(true)
            })
        return () => { active = false }
    }, [enabled, key, setData])

    useEffect(() => {
        if (!enabled || !loaded) return
        const draft = Object.fromEntries(
            Object.entries(data).filter(([field]) => !excludedRef.current.includes(field))
        )
        setStatus('Modifications en cours…')
        const saveDraft = () => fetch('/form-drafts/', {
                method: 'POST',
                credentials: 'same-origin',
                keepalive: true,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': decodeURIComponent(csrfToken()),
                },
                body: JSON.stringify({ key, data: draft }),
            })
        timeoutRef.current = window.setTimeout(() => {
            timeoutRef.current = null
            pendingSaveRef.current = saveDraft()
            pendingSaveRef.current
                .then((response) => {
                    if (!response.ok) throw new Error('draft save failed')
                    setStatus('Brouillon enregistré automatiquement')
                })
                .catch(() => setStatus('Sauvegarde automatique indisponible'))
        }, 700)
        window.addEventListener('pagehide', saveDraft)
        return () => {
            if (timeoutRef.current !== null) window.clearTimeout(timeoutRef.current)
            timeoutRef.current = null
            window.removeEventListener('pagehide', saveDraft)
        }
    }, [data, enabled, key, loaded])

    const clearDraft = async () => {
        if (timeoutRef.current !== null) window.clearTimeout(timeoutRef.current)
        timeoutRef.current = null
        if (pendingSaveRef.current) await pendingSaveRef.current.catch(() => undefined)
        return fetch('/form-drafts/', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': decodeURIComponent(csrfToken()),
            },
            body: JSON.stringify({ key, delete: true }),
        })
    }

    return { autosaveStatus: status, clearDraft }
}
