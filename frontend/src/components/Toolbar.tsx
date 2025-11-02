import Button from './atoms/Button'

type Props = {
  onCompare: () => void
  onExportPdf: () => void
  onExportDocx: () => void
  disabledCompare?: boolean
  disabledExport?: boolean
}

export function Toolbar({ onCompare, onExportPdf, onExportDocx, disabledCompare, disabledExport }: Props) {
  return (
    <div className="flex gap-2">
      <Button onClick={onCompare} disabled={disabledCompare}>Compare</Button>
      <Button variant="secondary" onClick={onExportPdf} disabled={disabledExport}>Export PDF</Button>
      <Button variant="secondary" onClick={onExportDocx} disabled={disabledExport}>Export Word</Button>
    </div>
  )
}


