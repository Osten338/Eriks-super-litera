import { useRef } from 'react'

type Props = {
  original?: File | null
  modified?: File | null
  onChange: (k: 'original' | 'modified', f: File | null) => void
}

export function UploadPane({ original, modified, onChange }: Props) {
  const originalRef = useRef<HTMLInputElement>(null)
  const modifiedRef = useRef<HTMLInputElement>(null)

  return (
    <div className="space-y-4">
      <div>
        <label className="text-sm font-medium">Original (.docx/.pdf)</label>
        <input
          ref={originalRef}
          type="file"
          accept=".docx,.pdf"
          className="mt-1 block w-full text-sm"
          onChange={(e) => onChange('original', e.target.files?.[0] || null)}
        />
      </div>
      <div>
        <label className="text-sm font-medium">Modified (.docx/.pdf)</label>
        <input
          ref={modifiedRef}
          type="file"
          accept=".docx,.pdf"
          className="mt-1 block w-full text-sm"
          onChange={(e) => onChange('modified', e.target.files?.[0] || null)}
        />
      </div>
    </div>
  )
}


