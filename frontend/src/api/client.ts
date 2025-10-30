import axios from 'axios'
import type { DiffResponse, Stats } from './types'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function compareDocuments(
  original: File,
  modified: File,
  options: { includeFormatting: boolean; ocr?: boolean }
): Promise<DiffResponse> {
  const form = new FormData()
  form.append('original', original)
  form.append('modified', modified)
  form.append('options', JSON.stringify(options))
  const { data } = await axios.post(`${BASE_URL}/compare`, form)
  return data as DiffResponse
}

export async function exportPdf(diffHtmlByParagraph: string[], stats: Stats, meta: Record<string, unknown>) {
  const { data } = await axios.post(
    `${BASE_URL}/export/pdf`,
    { diffHtmlByParagraph, stats, meta },
    { responseType: 'blob' }
  )
  return data as Blob
}

export async function exportDocx(diffHtmlByParagraph: string[], stats: Stats, meta: Record<string, unknown>) {
  const { data } = await axios.post(
    `${BASE_URL}/export/docx`,
    { diffHtmlByParagraph, stats, meta },
    { responseType: 'blob' }
  )
  return data as Blob
}


