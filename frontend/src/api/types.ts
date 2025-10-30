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


