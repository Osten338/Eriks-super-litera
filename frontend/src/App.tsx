import { Suspense, lazy, useEffect, useMemo, useState } from 'react'
import { Header } from './components/Header'
import { UploadPane } from './components/UploadPane'
import { SettingsPane } from './components/SettingsPane'
import { Toolbar } from './components/Toolbar'
const RedlinePreview = lazy(() => import('./components/RedlinePreview').then(m => ({ default: m.RedlinePreview })))
const Summary = lazy(() => import('./components/Summary').then(m => ({ default: m.Summary })))
const EasterEgg = lazy(() => import('./components/EasterEgg').then(m => ({ default: m.EasterEgg })))
import { compareDocuments, exportDocx, exportPdf, exportPdfFromDocx, exportDocxFromOOXML } from './api/client'
import type { DiffResponse, DiffResponseOOXML } from './api/types'
const Hero = lazy(() => import('./components/organisms/Hero'))
const FeatureGrid = lazy(() => import('./components/organisms/FeatureGrid'))
const Footer = lazy(() => import('./components/organisms/Footer'))

function App() {
  const [original, setOriginal] = useState<File | null>(null)
  const [modified, setModified] = useState<File | null>(null)
  const [includeFormatting, setIncludeFormatting] = useState(true)
  const [ocr, setOcr] = useState(true)
  const [diff, setDiff] = useState<DiffResponse | DiffResponseOOXML | null>(null)
  const [loading, setLoading] = useState(false)
  const [exporting, setExporting] = useState<null | 'pdf' | 'docx'>(null)

  async function onCompare() {
    if (!original || !modified) return
    setLoading(true)
    try {
      const res = await compareDocuments(original, modified, { includeFormatting, ocr })
      setDiff(res)
    } finally {
      setLoading(false)
    }
  }

  async function onExportPdf() {
    if (!diff || exporting) return
    try {
      setExporting('pdf')
      
      // Check if this is OOXML response
      if ('document_bytes' in diff) {
        // OOXML mode: export PDF from DOCX
        const blob = await exportPdfFromDocx(diff.document_bytes)
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'redline.pdf'
        document.body.appendChild(a)
        a.click()
        a.remove()
        URL.revokeObjectURL(url)
      } else {
        // Legacy HTML mode
        const blob = await exportPdf(diff.paragraphs.map(p => p.html), diff.stats, diff.meta)
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'compare.pdf'
        document.body.appendChild(a)
        a.click()
        a.remove()
        URL.revokeObjectURL(url)
      }
    } catch (err) {
      console.error('Export PDF failed', err)
      alert('Export PDF failed. Please ensure the backend is running on http://localhost:8000 and try again.')
    } finally {
      setExporting(null)
    }
  }

  async function onExportDocx() {
    if (!diff || exporting) return
    try {
      setExporting('docx')
      
      // Check if this is OOXML response
      if ('document_bytes' in diff) {
        // OOXML mode: export DOCX directly
        const blob = await exportDocxFromOOXML(diff.document_bytes)
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'redline.docx'
        document.body.appendChild(a)
        a.click()
        a.remove()
        URL.revokeObjectURL(url)
      } else {
        // Legacy HTML mode
        if (!original) return
        const blob = await exportDocx(original, diff.paragraphs.map(p => p.html), diff.stats, diff.meta)
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'compare.docx'
        document.body.appendChild(a)
        a.click()
        a.remove()
        URL.revokeObjectURL(url)
      }
    } catch (err: any) {
      console.error('Export DOCX failed', err)
      try {
        // Axios error responses with responseType 'blob' need manual decoding
        // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
        const blob = err?.response?.data as Blob | undefined
        const text = blob ? await new Response(blob).text() : ''
        alert(text || 'Export Word failed. Please ensure the backend is running on http://localhost:8000 and try again.')
      } catch {
        alert('Export Word failed. Please ensure the backend is running on http://localhost:8000 and try again.')
      }
    } finally {
      setExporting(null)
    }
  }

  // very light hash-based routing
  const [route, setRoute] = useState<string>(window.location.hash.replace('#', '') || '/')
  useEffect(() => {
    const handler = () => setRoute(window.location.hash.replace('#', '') || '/')
    window.addEventListener('hashchange', handler)
    return () => window.removeEventListener('hashchange', handler)
  }, [])

  const goToApp = () => {
    window.location.hash = '/app'
  }

  const features = useMemo(() => ([
    { title: 'Crystal-clear redlines', description: 'Readable insertions, deletions and moves, optimized for legal docs.' },
    { title: 'Fast & accurate', description: 'Optimized diff engine returns results in seconds.' },
    { title: 'Export your way', description: 'Beautiful PDFs and DOCX exports that preserve structure.' },
    { title: 'Secure by default', description: 'Files are processed safely and never shared.' },
  ]), [])

  if (route !== '/app') {
    return (
      <div className="min-h-full flex flex-col p-4 gap-8">
        <Header />
      <main id="main" className="max-w-6xl w-full mx-auto flex-1 space-y-8">
          <Suspense>
            <Hero onPrimary={goToApp} />
            <FeatureGrid items={features} />
            <Footer />
          </Suspense>
        </main>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      <Header />
      <main id="main" className="flex-1 grid grid-cols-12 gap-4 p-4">
        <aside className="col-span-12 lg:col-span-4 space-y-6">
          <UploadPane original={original || undefined} modified={modified || undefined} onChange={(k, f) => (k === 'original' ? setOriginal(f) : setModified(f))} />
          <SettingsPane includeFormatting={includeFormatting} setIncludeFormatting={setIncludeFormatting} ocr={ocr} setOcr={setOcr} />
          <Toolbar
            onCompare={onCompare}
            onExportPdf={onExportPdf}
            onExportDocx={onExportDocx}
            disabledCompare={loading || !original || !modified}
            disabledExport={loading || !diff || !!exporting}
          />
          {diff && <Summary {...diff.stats} />}
        </aside>
        <section className="col-span-12 lg:col-span-8">
          {!diff && (
            <div className="rounded-xl border border-white/10 bg-white/5 p-6 text-sm text-white/70">
              Upload two files and click Compare.
            </div>
          )}
          <Suspense>
            {diff && 'paragraphs' in diff && <RedlinePreview paragraphs={diff.paragraphs} />}
            {diff && !('paragraphs' in diff) && (
              <div className="rounded-xl border border-white/10 bg-white/5 p-6 text-sm text-white/70">
                <p>OOXML mode: Document compared successfully with {diff.stats.total} change{diff.stats.total !== 1 ? 's' : ''}.</p>
                <p className="mt-2">Use the export buttons to download the revision-tracked DOCX or PDF.</p>
              </div>
            )}
            {diff && <EasterEgg total={diff.stats.total} />}
          </Suspense>
        </section>
      </main>
    </div>
  )
}

export default App


