type Props = {
  paragraphs: { html: string }[]
}

export function RedlinePreview({ paragraphs }: Props) {
  return (
    <div className="pr-2">
      <div className="mb-2 text-xs text-white/60">Preview</div>
      <div className="rounded-xl border border-white/10 bg-white/5 p-3 max-h-[70vh] overflow-auto">
        {paragraphs.map((p, i) => (
          <div key={i} className="text-sm" dangerouslySetInnerHTML={{ __html: p.html }} />
        ))}
      </div>
    </div>
  )
}


