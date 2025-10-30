type Props = {
  onCompare: () => void
  onExportPdf: () => void
  onExportDocx: () => void
  disabled?: boolean
}

export function Toolbar({ onCompare, onExportPdf, onExportDocx, disabled }: Props) {
  return (
    <div className="flex gap-2">
      <button className="px-3 py-1.5 bg-black text-white rounded text-sm" onClick={onCompare} disabled={disabled}>Compare</button>
      <button className="px-3 py-1.5 border rounded text-sm" onClick={onExportPdf} disabled={disabled}>Export PDF</button>
      <button className="px-3 py-1.5 border rounded text-sm" onClick={onExportDocx} disabled={disabled}>Export Word</button>
    </div>
  )
}


