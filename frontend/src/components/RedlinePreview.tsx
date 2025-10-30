import DOMPurify from 'dompurify'

type Props = {
  paragraphs: { html: string }[]
}

export function RedlinePreview({ paragraphs }: Props) {
  return (
    <div className="space-y-2 overflow-auto max-h-[70vh] pr-2">
      {paragraphs.map((p, i) => (
        <div key={i} className="text-sm" dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(p.html) }} />
      ))}
    </div>
  )
}


