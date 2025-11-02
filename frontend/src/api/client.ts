import axios from 'axios'
import type { DiffResponse, DiffResponseOOXML, Stats, CompareOptions } from './types'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function compareDocuments(
  original: File,
  modified: File,
  options: CompareOptions = {}
): Promise<DiffResponse | DiffResponseOOXML> {
  const form = new FormData()
  form.append('original', original)
  form.append('modified', modified)
  
  // Default to docx_ooxml mode for DOCX files
  const defaultOptions: CompareOptions = {
    mode: 'docx_ooxml',
    includeFormatting: true,
    ocr: true,
    ...options,
  }
  
  form.append('options', JSON.stringify(defaultOptions))
  const { data } = await axios.post(`${BASE_URL}/compare`, form)
  return data
}

export async function exportPdf(diffHtmlByParagraph: string[], stats: Stats, meta: Record<string, unknown>) {
  const { data } = await axios.post(
    `${BASE_URL}/export/pdf`,
    { diffHtmlByParagraph, stats, meta },
    { responseType: 'blob' }
  )
  return data as Blob
}

export async function exportDocx(
  original: File,
  diffHtmlByParagraph: string[],
  stats: Stats,
  meta: Record<string, unknown>
) {
  const form = new FormData()
  form.append('original', original)
  form.append('payload', JSON.stringify({ diffHtmlByParagraph, stats, meta }))
  const { data } = await axios.post(`${BASE_URL}/export/docx`, form, { responseType: 'blob' })
  return data as Blob
}

export async function exportPdfFromDocx(docxBytesB64: string, options: CompareOptions = {}) {
  const { data } = await axios.post(
    `${BASE_URL}/export/pdf-from-docx`,
    {
      docx_bytes_b64: docxBytesB64,
      options: JSON.stringify(options),
    },
    { responseType: 'blob' }
  )
  return data as Blob
}

export async function exportDocxFromOOXML(docxBytesB64: string) {
  const { data } = await axios.post(
    `${BASE_URL}/export/docx-from-ooxml`,
    { docx_bytes_b64: docxBytesB64 },
    { responseType: 'blob' }
  )
  return data as Blob
}


