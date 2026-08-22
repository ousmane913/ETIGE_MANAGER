import React from 'react'
import { createRoot } from 'react-dom/client'
import { createInertiaApp } from '@inertiajs/react'
import axios from 'axios'
import './styles.css'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

const pages = import.meta.glob('./pages/**/*.tsx', { eager: true }) as Record<string, { default: React.ComponentType<any> }>
createInertiaApp({
  resolve: (name) => pages[`./pages/${name}.tsx`],
  setup({ el, App, props }) { createRoot(el).render(<App {...props} />) },
})