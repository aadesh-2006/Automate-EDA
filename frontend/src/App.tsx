import { useEffect, useMemo, useRef, useState } from 'react'
import {
  Activity, AlertCircle, ArrowDownToLine, ArrowRight, BarChart3, Check,
  CheckCircle2, ChevronDown, CircleHelp, Database, FileChartColumn,
  FileSpreadsheet, FileText, FlaskConical, Gauge, Layers3, LoaderCircle,
  Menu, RefreshCw, Search, ShieldCheck, Sparkles, Upload, WandSparkles, X,
} from 'lucide-react'
import {
  Cell, Pie, PieChart, ResponsiveContainer,
  Tooltip,
} from 'recharts'
import {
  edaApi, errorMessage,
  type AIInsights, type DataQuality, type DatasetProfile, type InsightEvidence,
} from './lib/api'
import './App.css'

type Tab = 'overview' | 'quality' | 'visualizations' | 'insights'
type VizKind = 'histogram' | 'box-plot' | 'correlation-heatmap'
type VizResult = { kind: VizKind; url: string; column?: string }

const demoCsv = `date,region,revenue,orders,customers,satisfaction
2026-01-01,North,12500,128,98,4.2
2026-01-02,South,14800,142,110,4.5
2026-01-03,East,11200,105,88,3.9
2026-01-04,West,16900,160,126,4.7
2026-01-05,North,13700,132,101,4.3
2026-01-06,South,15400,151,115,4.6
2026-01-07,East,9800,94,79,3.7
2026-01-08,West,18300,177,139,4.8
2026-01-09,North,14200,138,106,4.4
2026-01-10,South,16100,157,120,4.6
2026-01-11,East,10500,101,84,3.8
2026-01-12,West,19200,184,145,4.9
2026-01-13,North,15100,145,111,4.5
2026-01-14,South,17200,166,128,4.7
2026-01-15,East,11900,113,92,4.0
2026-01-16,West,20100,192,151,4.9
`

const money = (n: number) => new Intl.NumberFormat('en-IN', {
  notation: n >= 100000 ? 'compact' : 'standard',
  maximumFractionDigits: 1,
}).format(n)

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

function MarkdownText({ text }: { text: string }) {
  return (
    <div className="markdown-body">
      {text.split('\n').map((line, index) => {
        const value = line.trim()
        if (!value) return <div className="markdown-space" key={index} />
        if (value.startsWith('### ')) return <h4 key={index}>{value.slice(4)}</h4>
        if (value.startsWith('## ')) return <h3 key={index}>{value.slice(3)}</h3>
        if (value.startsWith('# ')) return <h3 key={index}>{value.slice(2)}</h3>
        if (/^[-*]\s/.test(value)) return <p className="markdown-bullet" key={index}>• {value.slice(2)}</p>
        if (/^\d+\.\s/.test(value)) return <p className="markdown-bullet" key={index}>{value}</p>
        return <p key={index}>{value.replace(/\*\*(.*?)\*\*/g, '$1')}</p>
      })}
    </div>
  )
}

function App() {
  const [csv, setCsv] = useState('')
  const [filename, setFilename] = useState('')
  const [profile, setProfile] = useState<DatasetProfile | null>(null)
  const [quality, setQuality] = useState<DataQuality | null>(null)
  const [evidence, setEvidence] = useState<InsightEvidence | null>(null)
  const [ai, setAi] = useState<AIInsights | null>(null)
  const [tab, setTab] = useState<Tab>('overview')
  const [selectedColumn, setSelectedColumn] = useState('')
  const [visuals, setVisuals] = useState<VizResult[]>([])
  const [busy, setBusy] = useState('')
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [apiOnline, setApiOnline] = useState<boolean | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const fileInput = useRef<HTMLInputElement>(null)

  const numericColumns = useMemo(
    () => profile?.columns.filter((column) => /int|float|double|number/i.test(column.dtype)).map((column) => column.name) ?? [],
    [profile],
  )

  useEffect(() => {
    edaApi.health().then(() => setApiOnline(true)).catch(() => setApiOnline(false))
  }, [])

  useEffect(() => () => visuals.forEach((item) => URL.revokeObjectURL(item.url)), [visuals])

  async function analyze(content: string, name: string) {
    setBusy('analyze')
    setError('')
    setNotice('')
    setAi(null)
    setVisuals((old) => {
      old.forEach((item) => URL.revokeObjectURL(item.url))
      return []
    })
    setProfile(null)
    setQuality(null)
    setEvidence(null)
    try {
      const [profileResult, qualityResult, evidenceResult] = await Promise.all([
        edaApi.profile(content),
        edaApi.quality(content),
        edaApi.evidence(content),
      ])
      setCsv(content)
      setFilename(name)
      setProfile(profileResult.data)
      setQuality(qualityResult.data)
      setEvidence(evidenceResult.data)
      setSelectedColumn(
        profileResult.data.columns.find((column) => /int|float|double|number/i.test(column.dtype))?.name
        ?? profileResult.data.column_names[0] ?? '',
      )
      setTab('overview')
      setNotice('Dataset profiled successfully. Your data stays in this session.')
      setApiOnline(true)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy('')
    }
  }

  async function handleFile(file?: File) {
    if (!file) return
    if (!file.name.toLowerCase().endsWith('.csv')) {
      setError('Please upload a .csv file.')
      return
    }
    if (file.size > 25 * 1024 * 1024) {
      setError('This interface accepts CSV files up to 25 MB.')
      return
    }
    const content = await file.text()
    if (!content.trim()) {
      setError('The selected file is empty.')
      return
    }
    await analyze(content, file.name)
  }

  async function loadDemo() {
    await analyze(demoCsv, 'sample-sales-data.csv')
  }

  async function generateInsights() {
    if (!csv) return
    setBusy('insights')
    setError('')
    try {
      const result = await edaApi.insights(csv)
      setAi(result.data)
      setTab('insights')
      setNotice('AI insights generated from the dataset evidence.')
    } catch (err) {
      setError(`AI insights could not be generated: ${errorMessage(err)}`)
      setTab('insights')
    } finally {
      setBusy('')
    }
  }

  async function generateVisualization(kind: VizKind) {
    if (!csv) return
    if (kind !== 'correlation-heatmap' && !selectedColumn) {
      setError('Choose a column before generating this chart.')
      return
    }
    setBusy(kind)
    setError('')
    try {
      const response = await edaApi.visualization(
        kind, csv, kind === 'correlation-heatmap' ? undefined : selectedColumn,
      )
      const url = URL.createObjectURL(response.data)
      setVisuals((old) => {
        old.filter((item) => item.kind === kind).forEach((item) => URL.revokeObjectURL(item.url))
        return [...old.filter((item) => item.kind !== kind), {
          kind, url, column: kind === 'correlation-heatmap' ? undefined : selectedColumn,
        }]
      })
      setTab('visualizations')
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy('')
    }
  }

  async function exportReport(kind: 'pdf' | 'html') {
    if (!csv) return
    setBusy(`report-${kind}`)
    setError('')
    try {
      const response = await edaApi.report(kind, csv)
      downloadBlob(response.data, `datalens-eda-report.${kind}`)
      setNotice(`${kind.toUpperCase()} report downloaded.`)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy('')
    }
  }

  const navItems: { id: Tab; label: string; icon: typeof Activity }[] = [
    { id: 'overview', label: 'Overview', icon: Gauge },
    { id: 'quality', label: 'Data quality', icon: ShieldCheck },
    { id: 'visualizations', label: 'Visualizations', icon: BarChart3 },
    { id: 'insights', label: 'AI insights', icon: Sparkles },
  ]

  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="brand">
          <div className="brand-mark"><Layers3 size={22} strokeWidth={2.5} /></div>
          <div><strong>DataLens<span> AI</span></strong><small>DATA INTELLIGENCE</small></div>
          <button className="icon-button mobile-close" aria-label="Close menu" onClick={() => setSidebarOpen(false)}><X size={19} /></button>
        </div>

        <div className="workspace-label">WORKSPACE</div>
        <button className="workspace-select" onClick={() => fileInput.current?.click()}>
          <div className="workspace-avatar">A</div>
          <span><strong>My workspace</strong><small>Personal project</small></span>
          <ChevronDown size={15} />
        </button>

        <div className="nav-label">ANALYZE</div>
        <nav className="sidebar-nav" aria-label="Main navigation">
          {navItems.map((item) => {
            const Icon = item.icon
            return <button key={item.id} className={`nav-item ${tab === item.id ? 'active' : ''}`} onClick={() => { setTab(item.id); setSidebarOpen(false) }}>
              <Icon size={18} /><span>{item.label}</span>
              {item.id === 'insights' && <span className="nav-new">AI</span>}
            </button>
          })}
        </nav>

        <div className="sidebar-divider" />
        <div className="nav-label">YOUR DATA</div>
        <div className="dataset-side-card">
          <div className="file-icon"><FileSpreadsheet size={17} /></div>
          <div className="dataset-side-copy">
            <strong>{filename || 'No dataset yet'}</strong>
            <small>{profile ? `${money(profile.rows)} rows · ${profile.columns_count} columns` : 'Upload a CSV to begin'}</small>
          </div>
          {profile && <CheckCircle2 className="side-check" size={16} />}
        </div>
        <button className="sidebar-upload" onClick={() => fileInput.current?.click()}><Upload size={16} /> Upload dataset</button>

        <div className="sidebar-spacer" />
        <div className="sidebar-bottom">
          <div className="api-status">
            <span className={`status-dot ${apiOnline ? 'online' : apiOnline === false ? 'offline' : ''}`} />
            <span>Backend API</span>
            <strong>{apiOnline ? 'Connected' : apiOnline === false ? 'Offline' : 'Checking'}</strong>
          </div>
          <a className="github-link" href="https://github.com/aadesh-2006/Automate-EDA" target="_blank" rel="noreferrer"><Layers3 size={16} /> Project repository <ArrowRight size={14} /></a>
          <div className="sidebar-version">DataLens AI <span>v0.1.0</span></div>
        </div>
      </aside>

      {sidebarOpen && <button className="sidebar-overlay" aria-label="Close navigation" onClick={() => setSidebarOpen(false)} />}

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumb">
            <button className="icon-button mobile-menu" aria-label="Open menu" onClick={() => setSidebarOpen(true)}><Menu size={20} /></button>
            <span>Workspace</span><span className="crumb-separator">/</span><strong>{navItems.find((item) => item.id === tab)?.label ?? 'Overview'}</strong>
          </div>
          <div className="topbar-actions">
            <span className="private-label"><ShieldCheck size={15} /> Session workspace</span>
            <button className="button button-quiet button-small" onClick={() => fileInput.current?.click()}><Upload size={15} /> Upload CSV</button>
          </div>
        </header>

        <div className="page-content">
          <section className="page-heading">
            <div>
              <div className="eyebrow"><span className="eyebrow-dot" /> AUTOMATED EXPLORATORY DATA ANALYSIS</div>
              <h1>{tab === 'overview' ? 'Your data, in focus.' : navItems.find((item) => item.id === tab)?.label}</h1>
              <p className="page-subtitle">{tab === 'overview' ? 'Turn raw CSV files into clear, actionable understanding.' : tab === 'quality' ? 'Understand missingness, duplicates, and structural issues.' : tab === 'visualizations' ? 'Explore distributions and relationships in your data.' : 'Evidence-grounded analysis, with AI doing the interpretation.'}</p>
            </div>
            {profile && <div className="dataset-pill"><span className="pill-dot" /><FileSpreadsheet size={15} /> <span>{filename}</span></div>}
          </section>

          {error && <div className="alert alert-error" role="alert"><AlertCircle size={18} /><span>{error}</span><button aria-label="Dismiss error" onClick={() => setError('')}><X size={16} /></button></div>}
          {notice && !error && <div className="alert alert-success" role="status"><CheckCircle2 size={17} /><span>{notice}</span><button aria-label="Dismiss notification" onClick={() => setNotice('')}><X size={16} /></button></div>}

          {!profile ? (
            <section className="welcome-grid">
              <div className="upload-panel">
                <div className="upload-panel-top"><div className="upload-symbol"><FileChartColumn size={24} /></div><span className="step-chip">GET STARTED</span></div>
                <h2>Make sense of your data.</h2>
                <p className="upload-intro">Drop in a CSV and get a complete data profile, quality checks, visualizations, and AI-assisted insights.</p>
                <button className="drop-zone" onClick={() => fileInput.current?.click()} onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); void handleFile(event.dataTransfer.files[0]) }}>
                  <div className="upload-circle"><Upload size={23} /></div>
                  <strong>Click to upload or drop your file</strong>
                  <span>CSV files only · Up to 25 MB</span>
                  <span className="choose-file">Choose a CSV file <ArrowRight size={14} /></span>
                </button>
                <div className="or-divider"><span /> OR <span /></div>
                <button className="button button-secondary sample-button" disabled={!!busy} onClick={() => void loadDemo()}>{busy === 'analyze' ? <LoaderCircle className="spin" size={17} /> : <FlaskConical size={17} />} Explore with sample data</button>
                <p className="privacy-note"><ShieldCheck size={14} /> Data is processed by your configured backend.</p>
              </div>
              <div className="welcome-right">
                <div className="welcome-visual">
                  <div className="visual-orbit orbit-one" /><div className="visual-orbit orbit-two" />
                  <div className="visual-core"><Layers3 size={33} /></div>
                  <div className="float-card float-card-a"><div className="float-icon float-purple"><BarChart3 size={16} /></div><span><strong>Data profiling</strong><small>Structure & statistics</small></span><Check size={16} className="float-check" /></div>
                  <div className="float-card float-card-b"><div className="float-icon float-green"><ShieldCheck size={16} /></div><span><strong>Quality checks</strong><small>Issues surfaced early</small></span><Check size={16} className="float-check" /></div>
                  <div className="float-card float-card-c"><div className="float-icon float-blue"><Sparkles size={16} /></div><span><strong>AI interpretation</strong><small>Grounded in evidence</small></span><ArrowRight size={15} /></div>
                  <div className="visual-caption"><span className="caption-line" /> ONE WORKSPACE. BETTER QUESTIONS.</div>
                </div>
                <div className="feature-list">
                  <div><span className="feature-check"><Check size={14} /></span><span><strong>Instant profiling</strong><small>Dimensions, types, and summary statistics</small></span></div>
                  <div><span className="feature-check"><Check size={14} /></span><span><strong>Quality diagnostics</strong><small>Missing data, duplicates, and anomalies in structure</small></span></div>
                  <div><span className="feature-check"><Check size={14} /></span><span><strong>Reports that travel</strong><small>Export your findings as PDF or HTML</small></span></div>
                </div>
              </div>
            </section>
          ) : (
            <>
              <section className="dataset-toolbar">
                <div className="toolbar-file"><div className="toolbar-file-icon"><FileSpreadsheet size={18} /></div><div><strong>{filename}</strong><small>CSV dataset <span className="bullet-separator">·</span> {money(profile.rows)} records</small></div></div>
                <div className="toolbar-actions">
                  <button className="button button-quiet button-small" disabled={!!busy} onClick={() => void analyze(csv, filename)}><RefreshCw size={14} /> Refresh</button>
                  <button className="button button-secondary button-small" disabled={!!busy} onClick={() => void exportReport('html')}><FileText size={14} /> HTML</button>
                  <button className="button button-primary button-small" disabled={!!busy} onClick={() => void exportReport('pdf')}>{busy === 'report-pdf' ? <LoaderCircle className="spin" size={14} /> : <ArrowDownToLine size={14} />} Export PDF</button>
                </div>
              </section>

              <section className="metrics-grid">
                <MetricCard label="Total records" value={money(profile.rows)} detail="Rows in dataset" icon={Database} tone="purple" />
                <MetricCard label="Total features" value={String(profile.columns_count)} detail="Columns detected" icon={Layers3} tone="blue" />
                <MetricCard label="Missing values" value={money(profile.missing_values_total)} detail={profile.rows && profile.columns_count ? `${((profile.missing_values_total / (profile.rows * profile.columns_count)) * 100).toFixed(2)}% of cells` : 'No cells detected'} icon={AlertCircle} tone={profile.missing_values_total ? 'orange' : 'green'} />
                <MetricCard label="Duplicate rows" value={money(profile.duplicate_rows)} detail={profile.rows ? `${((profile.duplicate_rows / profile.rows) * 100).toFixed(2)}% of records` : 'No records'} icon={FileSpreadsheet} tone={profile.duplicate_rows ? 'orange' : 'green'} />
              </section>

              {tab === 'overview' && <Overview profile={profile} quality={quality} evidence={evidence} setTab={setTab} generateInsights={generateInsights} busy={busy} />}
              {tab === 'quality' && <QualityView profile={profile} quality={quality} evidence={evidence} />}
              {tab === 'visualizations' && <Visualizations profile={profile} numericColumns={numericColumns} selectedColumn={selectedColumn} setSelectedColumn={setSelectedColumn} visuals={visuals} generate={generateVisualization} busy={busy} />}
              {tab === 'insights' && <InsightsView ai={ai} evidence={evidence} busy={busy} generate={generateInsights} />}
            </>
          )}

          <footer className="page-footer"><span><span className="footer-dot" /> Made for curious minds and cleaner data.</span><span>DataLens AI <span className="footer-separator">/</span> Built with FastAPI & React</span></footer>
        </div>
      </main>

      <input ref={fileInput} className="visually-hidden" type="file" accept=".csv,text/csv" onChange={(event) => { void handleFile(event.target.files?.[0]); event.currentTarget.value = '' }} />
    </div>
  )
}

function MetricCard({ label, value, detail, icon: Icon, tone }: {
  label: string; value: string; detail: string; icon: import('lucide-react').LucideIcon; tone: string
}) {
  return <article className="metric-card"><div className="metric-top"><span>{label}</span><div className={`metric-icon tone-${tone}`}><Icon size={18} /></div></div><div className="metric-value">{value}</div><div className="metric-detail"><span className={`detail-indicator ${tone}`} />{detail}</div></article>
}

function SectionHeader({ eyebrow, title, action }: { eyebrow?: string; title: string; action?: React.ReactNode }) {
  return <div className="section-heading"><div>{eyebrow && <div className="section-eyebrow">{eyebrow}</div>}<h2>{title}</h2></div>{action}</div>
}

function Overview({ profile, quality, evidence, setTab, generateInsights, busy }: {
  profile: DatasetProfile; quality: DataQuality | null; evidence: InsightEvidence | null
  setTab: (tab: Tab) => void; generateInsights: () => void; busy: string
}) {
  const typeCounts = profile.columns.reduce<Record<string, number>>((acc, col) => {
    const type = /int|float|double|number/i.test(col.dtype) ? 'Numeric' : /date|time/i.test(col.dtype) ? 'Date/time' : 'Text / category'
    acc[type] = (acc[type] ?? 0) + 1
    return acc
  }, {})
  const typeData = Object.entries(typeCounts).map(([name, value]) => ({ name, value }))
  const palette = ['#8b7cf6', '#5e9ff5', '#42c6a5']
  const statColumn = Object.keys(profile.numeric_summary)[0]
  const stats = statColumn ? profile.numeric_summary[statColumn] : null
  return <>
    <section className="overview-grid">
      <article className="panel schema-panel">
        <SectionHeader eyebrow="DATASET STRUCTURE" title="Column overview" action={<button className="text-action" onClick={() => setTab('quality')}>View quality <ArrowRight size={14} /></button>} />
        <div className="table-scroll"><table className="data-table"><thead><tr><th>Column name</th><th>Data type</th><th>Missing</th><th>Unique</th></tr></thead><tbody>{profile.columns.slice(0, 8).map((col) => <tr key={col.name}><td><span className="column-name"><span className="column-type-icon">{/int|float|double|number/i.test(col.dtype) ? '123' : 'Aa'}</span>{col.name}</span></td><td><span className="type-pill">{col.dtype}</span></td><td><span className={col.missing_values ? 'missing-value' : 'clean-value'}>{col.missing_values.toLocaleString()}</span></td><td>{col.unique_values.toLocaleString()}</td></tr>)}</tbody></table></div>
        {profile.columns.length > 8 && <button className="table-footer-action" onClick={() => setTab('quality')}>View all {profile.columns.length} columns <ArrowRight size={14} /></button>}
      </article>
      <article className="panel type-panel">
        <SectionHeader eyebrow="COMPOSITION" title="Column types" />
        <div className="type-chart-wrap"><ResponsiveContainer width="100%" height={174}><PieChart><Pie data={typeData} dataKey="value" nameKey="name" innerRadius={52} outerRadius={73} paddingAngle={4} stroke="none">{typeData.map((item, i) => <Cell key={item.name} fill={palette[i % palette.length]} />)}</Pie><Tooltip /></PieChart></ResponsiveContainer><div className="donut-center"><strong>{profile.columns_count}</strong><span>columns</span></div></div>
        <div className="type-legend">{typeData.map((item, i) => <div key={item.name}><span className="legend-dot" style={{ background: palette[i % palette.length] }} /><span>{item.name}</span><strong>{item.value}</strong></div>)}</div>
      </article>
    </section>

    <section className="overview-grid lower-grid">
      <article className="panel summary-panel">
        <SectionHeader eyebrow="NUMERIC PROFILE" title="Summary statistics" />
        {stats ? <><div className="summary-column-label"><Activity size={15} /> Showing <strong>{statColumn}</strong></div><div className="stats-grid">{[['Mean', stats.mean], ['Median', stats['50%']], ['Minimum', stats.min], ['Maximum', stats.max]].map(([label, value]) => <div className="stat-cell" key={String(label)}><span>{label}</span><strong>{typeof value === 'number' ? money(value) : '—'}</strong></div>)}</div><p className="muted-footnote">Quick summary for the first numeric feature. Full statistics are available in the exported report.</p></> : <EmptyState title="No numeric columns" detail="This dataset has no numeric features to summarize." />}
      </article>
      <article className="panel quality-summary-panel">
        <SectionHeader eyebrow="HEALTH CHECK" title="Data quality snapshot" action={<button className="text-action" onClick={() => setTab('quality')}>Full report <ArrowRight size={14} /></button>} />
        <div className="quality-summary-list"><QualityLine icon={AlertCircle} label="Missing values" value={profile.missing_values_total} good={profile.missing_values_total === 0} /><QualityLine icon={Layers3} label="Duplicate rows" value={profile.duplicate_rows} good={profile.duplicate_rows === 0} /><QualityLine icon={Gauge} label="Constant columns" value={quality?.constant_columns.length ?? 0} good={!quality?.constant_columns.length} /><QualityLine icon={Search} label="Mixed-type columns" value={quality?.mixed_type_columns.length ?? 0} good={!quality?.mixed_type_columns.length} /></div>
        {evidence && <div className="finding-note"><Sparkles size={15} /><span>{evidence.findings.length ? `${evidence.findings.length} evidence-based finding${evidence.findings.length === 1 ? '' : 's'} detected.` : 'No issues detected by the current quality checks.'}</span></div>}
      </article>
    </section>

    <section className="ai-callout">
      <div className="ai-callout-icon"><WandSparkles size={22} /></div>
      <div className="ai-callout-copy"><div className="ai-callout-eyebrow">YOUR DATA, INTERPRETED</div><h2>Ready for the “so what?”</h2><p>Generate AI-assisted findings grounded in the profile and data-quality evidence.</p></div>
      <button className="button button-light" onClick={generateInsights} disabled={!!busy}>{busy === 'insights' ? <LoaderCircle className="spin" size={16} /> : <Sparkles size={16} />} Generate insights <ArrowRight size={15} /></button>
    </section>
  </>
}

function QualityLine({ icon: Icon, label, value, good }: { icon: typeof Activity; label: string; value: number; good: boolean }) {
  return <div className="quality-line"><span className={`quality-line-icon ${good ? 'is-good' : 'is-warning'}`}><Icon size={16} /></span><span>{label}</span><strong>{value.toLocaleString()}</strong><span className={`quality-status ${good ? 'status-good' : 'status-warning'}`}>{good ? 'Clear' : 'Review'}</span></div>
}

function QualityView({ profile, quality, evidence }: { profile: DatasetProfile; quality: DataQuality | null; evidence: InsightEvidence | null }) {
  if (!quality) return <EmptyState title="Quality report unavailable" detail="Re-analyze your dataset to load the quality report." />
  return <>
    <section className="metrics-grid quality-metrics"><MetricCard label="Missing cells" value={money(quality.missing_values_total)} detail="Null or empty values" icon={AlertCircle} tone={quality.missing_values_total ? 'orange' : 'green'} /><MetricCard label="Duplicate rows" value={money(quality.duplicate_rows)} detail="Repeated complete records" icon={Layers3} tone={quality.duplicate_rows ? 'orange' : 'green'} /><MetricCard label="Constant features" value={String(quality.constant_columns.length)} detail="Only one distinct value" icon={Database} tone={quality.constant_columns.length ? 'orange' : 'green'} /><MetricCard label="Mixed types" value={String(quality.mixed_type_columns.length)} detail="Numeric and text values" icon={Activity} tone={quality.mixed_type_columns.length ? 'orange' : 'green'} /></section>
    <article className="panel quality-table-panel"><SectionHeader eyebrow="COLUMN-LEVEL DIAGNOSTICS" title="Quality by column" /><div className="table-scroll"><table className="data-table"><thead><tr><th>Column</th><th>Missing values</th><th>Missing %</th><th>Unique values</th><th>Uniqueness</th><th>Type</th></tr></thead><tbody>{quality.columns.map((col) => { const profileCol = profile.columns.find((item) => item.name === col.column); return <tr key={col.column}><td><strong>{col.column}</strong></td><td>{col.missing_values}</td><td><div className="percentage-cell"><div className="mini-progress"><span style={{ width: `${Math.min(100, col.missing_percentage)}%` }} /></div><span>{col.missing_percentage.toFixed(2)}%</span></div></td><td>{col.unique_values}</td><td>{(col.unique_ratio * 100).toFixed(1)}%</td><td><span className="type-pill">{profileCol?.dtype ?? 'unknown'}</span></td></tr>})}</tbody></table></div></article>
    <section className="quality-findings-grid">
      <FindingCard title="Constant columns" detail="Features with only one non-missing unique value." items={quality.constant_columns} />
      <FindingCard title="High cardinality" detail="Features where unique values meet the configured threshold." items={quality.high_cardinality_columns.map((item) => `${item.column} (${(item.unique_ratio * 100).toFixed(0)}% unique)`)} />
      <FindingCard title="Mixed types" detail="Text-like columns containing both numeric-looking and non-numeric values." items={quality.mixed_type_columns} />
    </section>
    <article className="panel evidence-panel"><SectionHeader eyebrow="DETERMINISTIC ANALYSIS" title="Evidence findings" />{evidence?.findings.length ? evidence.findings.map((finding, index) => <div className="evidence-row" key={`${finding.type}-${index}`}><span className={`finding-severity severity-${finding.severity}`}>{finding.severity}</span><div><strong>{finding.type.replace(/_/g, ' ')}</strong><p>{findingSummary(finding)}</p></div></div>) : <EmptyState title="No findings detected" detail="The deterministic checks did not detect any issues in this dataset." />}</article>
  </>
}

function FindingCard({ title, detail, items }: { title: string; detail: string; items: string[] }) {
  return <article className="panel finding-card"><div className="finding-card-title"><h3>{title}</h3><span className={items.length ? 'finding-count' : 'finding-count count-zero'}>{items.length}</span></div><p>{detail}</p>{items.length ? <ul>{items.slice(0, 8).map((item) => <li key={item}>{item}</li>)}</ul> : <div className="finding-empty"><CheckCircle2 size={15} /> None detected</div>}</article>
}

function findingSummary(finding: { type: string; evidence: Record<string, unknown> }) {
  if (finding.type === 'missing_values') return `${String(finding.evidence.count ?? 0)} missing values detected.`
  if (finding.type === 'duplicate_rows') return `${String(finding.evidence.count ?? 0)} duplicate rows detected.`
  if (finding.type === 'constant_columns') return `Columns: ${JSON.stringify(finding.evidence.columns ?? [])}`
  if (finding.type === 'high_cardinality') return `Columns: ${JSON.stringify(finding.evidence.columns ?? [])}`
  if (finding.type === 'mixed_types') return `Columns: ${JSON.stringify(finding.evidence.columns ?? [])}`
  return JSON.stringify(finding.evidence)
}

function Visualizations({ profile, numericColumns, selectedColumn, setSelectedColumn, visuals, generate, busy }: {
  profile: DatasetProfile; numericColumns: string[]; selectedColumn: string
  setSelectedColumn: (value: string) => void; visuals: VizResult[]
  generate: (kind: VizKind) => void; busy: string
}) {
  return <>
    <section className="panel viz-controls"><div><div className="section-eyebrow">EXPLORE YOUR DATA</div><h2>Build a visualization</h2><p>Select a numeric feature for a distribution chart, or inspect correlations across numeric columns.</p></div><div className="viz-select-wrap"><label htmlFor="viz-column">Numeric feature</label><select id="viz-column" value={selectedColumn} onChange={(event) => setSelectedColumn(event.target.value)} disabled={!numericColumns.length}>{numericColumns.map((column) => <option key={column}>{column}</option>)}</select></div></section>
    <section className="viz-action-grid">
      <VizAction icon={BarChart3} title="Histogram" detail="Inspect the distribution of values." onClick={() => generate('histogram')} busy={busy === 'histogram'} disabled={!numericColumns.length || !!busy} />
      <VizAction icon={Activity} title="Box plot" detail="Explore spread and potential outliers." onClick={() => generate('box-plot')} busy={busy === 'box-plot'} disabled={!numericColumns.length || !!busy} />
      <VizAction icon={Layers3} title="Correlation heatmap" detail="Compare relationships between numeric features." onClick={() => generate('correlation-heatmap')} busy={busy === 'correlation-heatmap'} disabled={!!busy} />
    </section>
    <section className="viz-results-grid">{visuals.map((visual) => <article className="panel viz-result" key={visual.kind}><div className="viz-result-heading"><div><h3>{visual.kind === 'histogram' ? 'Histogram' : visual.kind === 'box-plot' ? 'Box plot' : 'Correlation heatmap'}</h3><p>{visual.column ? `Feature: ${visual.column}` : 'Numeric feature relationships'}</p></div><a href={visual.url} download={`datalens-${visual.kind}.png`} className="icon-button" aria-label="Download chart"><ArrowDownToLine size={17} /></a></div><img src={visual.url} alt={`${visual.kind} chart`} /></article>)}</section>
    {!visuals.length && <EmptyState title="No visualizations yet" detail={`Generate a chart to explore your ${profile.columns_count} features.`} />}
  </>
}

function VizAction({ icon: Icon, title, detail, onClick, busy, disabled }: { icon: typeof Activity; title: string; detail: string; onClick: () => void; busy: boolean; disabled: boolean }) {
  return <button className="panel viz-action" onClick={onClick} disabled={disabled}><div className="viz-action-icon"><Icon size={20} /></div><div><strong>{title}</strong><p>{detail}</p></div><span className="viz-action-arrow">{busy ? <LoaderCircle className="spin" size={17} /> : <ArrowRight size={17} />}</span></button>
}

function InsightsView({ ai, evidence, busy, generate }: { ai: AIInsights | null; evidence: InsightEvidence | null; busy: string; generate: () => void }) {
  return <>
    <section className="ai-insights-banner"><div className="ai-banner-icon"><Sparkles size={23} /></div><div><div className="section-eyebrow">GROUNDED AI ANALYSIS</div><h2>From evidence to understanding.</h2><p>Insights use deterministic profiling and data-quality findings as their evidence source.</p></div><button className="button button-primary" onClick={generate} disabled={!!busy}>{busy === 'insights' ? <LoaderCircle className="spin" size={16} /> : <RefreshCw size={15} />}{ai ? 'Regenerate' : 'Generate insights'}</button></section>
    <section className="insights-grid"><article className="panel ai-report-panel"><SectionHeader eyebrow="AI INTERPRETATION" title="Analysis report" />{busy === 'insights' ? <div className="loading-state"><LoaderCircle className="spin" size={25} /><strong>Interpreting your dataset…</strong><p>Connecting to the configured language model.</p></div> : ai ? <MarkdownText text={ai.insights} /> : <EmptyState title="No AI report yet" detail="Generate insights to receive a concise interpretation of your dataset." />}</article><article className="panel insight-evidence-panel"><SectionHeader eyebrow="SOURCE OF TRUTH" title="Supporting findings" /><p className="panel-description">These checks are calculated from your CSV, independently of the language model.</p>{evidence?.findings.length ? evidence.findings.map((finding, index) => <div className="evidence-row" key={`${finding.type}-${index}`}><span className={`finding-severity severity-${finding.severity}`}>{finding.severity}</span><div><strong>{finding.type.replace(/_/g, ' ')}</strong><p>{findingSummary(finding)}</p></div></div>) : <EmptyState title="No flagged issues" detail="No findings were returned by the deterministic checks." />}</article></section>
    <div className="ai-disclaimer"><CircleHelp size={16} /><span>AI-generated interpretation can be incomplete. Verify important conclusions against the underlying data and evidence.</span></div>
  </>
}

function EmptyState({ title, detail }: { title: string; detail: string }) {
  return <div className="empty-state"><div className="empty-icon"><FileSpreadsheet size={20} /></div><strong>{title}</strong><p>{detail}</p></div>
}

export default App


