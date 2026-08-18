import React from 'react'
import { createRoot } from 'react-dom/client'
import { createInertiaApp } from '@inertiajs/react'
import './styles.css'

const pages = import.meta.glob('./pages/**/*.tsx', { eager: true }) as Record<string, { default: React.ComponentType<any> }>
createInertiaApp({
  resolve: (name) => pages[`./pages/${name}.tsx`],
  setup({ el, App, props }) { createRoot(el).render(<App {...props} />) },
})
