import { useMemo } from 'react'
import UploadCard from './molecules/UploadCard'

type Props = {
  original?: File | null
  modified?: File | null
  onChange: (k: 'original' | 'modified', f: File | null) => void
}

export function UploadPane({ original, modified, onChange }: Props) {
  const originalStatus = useMemo(() => (original ? 'ready' : 'idle'), [original])
  const modifiedStatus = useMemo(() => (modified ? 'ready' : 'idle'), [modified])

  return (
    <div className="space-y-3">
      <UploadCard
        label="Original (.docx/.pdf)"
        file={original || undefined}
        status={originalStatus}
        onFileSelect={(f) => onChange('original', f)}
      />
      <UploadCard
        label="Modified (.docx/.pdf)"
        file={modified || undefined}
        status={modifiedStatus}
        onFileSelect={(f) => onChange('modified', f)}
      />
    </div>
  )
}


