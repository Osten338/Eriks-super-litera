type Props = {
  includeFormatting: boolean
  setIncludeFormatting: (v: boolean) => void
  ocr: boolean
  setOcr: (v: boolean) => void
}

export function SettingsPane({ includeFormatting, setIncludeFormatting, ocr, setOcr }: Props) {
  return (
    <div className="space-y-3">
      <label className="flex items-center gap-2 text-sm">
        <input type="checkbox" checked={includeFormatting} onChange={(e) => setIncludeFormatting(e.target.checked)} />
        Include formatting differences
      </label>
      <label className="flex items-center gap-2 text-sm">
        <input type="checkbox" checked={ocr} onChange={(e) => setOcr(e.target.checked)} />
        OCR for scanned PDFs
      </label>
    </div>
  )
}


