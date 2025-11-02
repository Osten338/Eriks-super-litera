export type Stats = {
  insertions: number
  deletions: number
  moves: number
  total: number
}

export type DiffResponse = {
  paragraphs: { html: string }[]
  stats: Stats
  meta: Record<string, unknown>
}

export type DiffResponseOOXML = {
  document_bytes: string  // Base64 encoded
  stats: Stats
  meta: Record<string, unknown>
}

export type CompareOptions = {
  mode?: 'legacy_html' | 'docx_ooxml'
  shingle_size?: number
  jaccard_threshold?: number
  min_move_span_tokens?: number
  force_brand_colors?: boolean
  use_word_automation?: boolean
  includeFormatting?: boolean
  ocr?: boolean
  diffGranularity?: string
}


