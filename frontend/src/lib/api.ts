import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 120000,
})

export interface DatasetColumn {
  name: string
  dtype: string
  missing_values: number
  missing_percentage: number
  unique_values: number
}

export interface DatasetProfile {
  rows: number
  columns_count: number
  column_names: string[]
  columns: DatasetColumn[]
  missing_values_total: number
  duplicate_rows: number
  numeric_summary: Record<string, Record<string, number>>
}

export interface QualityColumn {
  column: string
  missing_values: number
  missing_percentage: number
  unique_values: number
  unique_ratio: number
}

export interface DataQuality {
  rows: number
  columns_count: number
  missing_values_total: number
  duplicate_rows: number
  constant_columns: string[]
  high_cardinality_columns: {
    column: string
    unique_values: number
    non_missing_values: number
    unique_ratio: number
  }[]
  mixed_type_columns: string[]
  columns: QualityColumn[]
  high_cardinality_threshold: number
}

export interface InsightFinding {
  type: string
  severity: string
  evidence: Record<string, unknown>
}

export interface InsightEvidence {
  dataset: DatasetProfile
  data_quality: DataQuality
  findings: InsightFinding[]
}

export interface AIInsights {
  dataset: DatasetProfile
  findings: InsightFinding[]
  insights: string
}

function csvConfig(csv: string) {
  return {
    data: csv,
    headers: { 'Content-Type': 'text/csv' },
  }
}

export const edaApi = {
  health: () => api.get('/health'),
  profile: (csv: string) =>
    api.post<DatasetProfile>('/api/v1/eda/profile', csv, {
      headers: { 'Content-Type': 'text/csv' },
    }),
  quality: (csv: string) =>
    api.post<DataQuality>('/api/v1/eda/data-quality', csv, {
      headers: { 'Content-Type': 'text/csv' },
    }),
  evidence: (csv: string) =>
    api.post<InsightEvidence>('/api/v1/eda/insights/evidence', csv, {
      headers: { 'Content-Type': 'text/csv' },
    }),
  insights: (csv: string) =>
    api.post<AIInsights>('/api/v1/eda/insights', csv, {
      headers: { 'Content-Type': 'text/csv' },
    }),
  visualization: (kind: 'histogram' | 'box-plot' | 'correlation-heatmap', csv: string, column?: string) =>
    api.post(
      `/api/v1/eda/visualizations/${kind}${column ? `?column=${encodeURIComponent(column)}` : ''}`,
      csv,
      { ...csvConfig(csv), responseType: 'blob' },
    ),
  report: (kind: 'pdf' | 'html', csv: string) =>
    api.post(`/api/v1/eda/report/${kind}`, csv, {
      headers: { 'Content-Type': 'text/csv' },
      responseType: 'blob',
    }),
}

export function errorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data
    if (detail instanceof Blob) {
      return `Request failed (${error.response?.status ?? 'network error'}). Check the API response and backend logs.`
    }
    if (typeof detail === 'object' && detail !== null && 'detail' in detail) {
      return String((detail as { detail: unknown }).detail)
    }
    if (!error.response) {
      return 'Cannot reach the DataLens API. Start the backend and try again.'
    }
    return error.message
  }
  return error instanceof Error ? error.message : 'An unexpected error occurred.'
}
