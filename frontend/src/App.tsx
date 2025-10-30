import { useState } from 'react'
import { Header } from './components/Header'
import { UploadPane } from './components/UploadPane'
import { SettingsPane } from './components/SettingsPane'
import { Toolbar } from './components/Toolbar'
import { RedlinePreview } from './components/RedlinePreview'
import { Summary } from './components/Summary'
import { EasterEgg } from './components/EasterEgg'
import { compareDocuments, exportDocx, exportPdf } from './api/client'
import type { DiffResponse } from './api/types'

function App() {
  const [original, setOriginal] = useState<File | null>(null)
  const [modified, setModified] = useState<File | null>(null)
  const [includeFormatting, setIncludeFormatting] = useState(true)
  const [ocr, setOcr] = useState(true)
  const [diff, setDiff] = useState<DiffResponse | null>(null)
  const [loading, setLoading] = useState(false)

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
    if (!diff) return
    const blob = await exportPdf(diff.paragraphs.map(p => p.html), diff.stats, diff.meta)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'compare.pdf'
    a.click()
    URL.revokeObjectURL(url)
  }

  async function onExportDocx() {
    if (!diff) return
    const blob = await exportDocx(diff.paragraphs.map(p => p.html), diff.stats, diff.meta)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'compare.docx'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="h-full flex flex-col">
      <Header />
      <main className="flex-1 grid grid-cols-12 gap-4 p-4">
        <aside className="col-span-4 border rounded p-3 space-y-6">
          <UploadPane original={original || undefined} modified={modified || undefined} onChange={(k, f) => (k === 'original' ? setOriginal(f) : setModified(f))} />
          <SettingsPane includeFormatting={includeFormatting} setIncludeFormatting={setIncludeFormatting} ocr={ocr} setOcr={setOcr} />
          <Toolbar onCompare={onCompare} onExportPdf={onExportPdf} onExportDocx={onExportDocx} disabled={loading || !original || !modified} />
          {diff && <Summary {...diff.stats} />}
        </aside>
        <section className="col-span-8 border rounded p-3">
          {!diff && <p className="text-sm text-gray-500">Upload two files and click Compare.</p>}
          {diff && <RedlinePreview paragraphs={diff.paragraphs} />}
          {diff && <EasterEgg total={diff.stats.total} />}
        </section>
      </main>
    </div>
  )
}

export default App


