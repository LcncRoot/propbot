import { useState } from 'react'
import { cn } from '@/lib/utils'
import { Opportunity, SearchFilters } from '@/types/opportunity'
import { NavItem } from './NavItem'
import { SearchInput } from './SearchInput'
import { Button } from './Button'
import { SearchResultsGrid } from './SearchResultsGrid'
import { FilterPanel } from './FilterPanel'
import { OpportunityDetail } from './OpportunityDetail'

// Icons
const HomeIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
    <polyline points="9 22 9 12 15 12 15 22" />
  </svg>
)

const FolderIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
  </svg>
)

const FileIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
    <polyline points="14 2 14 8 20 8" />
  </svg>
)

const RfiIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
    <line x1="12" y1="17" x2="12.01" y2="17" />
  </svg>
)

const StarIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
  </svg>
)

const SparkleIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5L12 3z" />
    <path d="M5 19l.5 1.5L7 21l-1.5.5L5 23l-.5-1.5L3 21l1.5-.5L5 19z" />
    <path d="M19 11l.5 1.5L21 13l-1.5.5L19 15l-.5-1.5L17 13l1.5-.5L19 11z" />
  </svg>
)

const FilterIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
  </svg>
)

const UserIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
    <circle cx="12" cy="7" r="4" />
  </svg>
)

const AnalyzeIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2a4 4 0 0 1 4 4c0 1.1-.45 2.1-1.17 2.83L12 12l-2.83-3.17A4 4 0 0 1 12 2z" />
    <path d="M12 12l2.83 3.17A4 4 0 1 1 12 22a4 4 0 0 1-2.83-6.83L12 12z" />
    <circle cx="12" cy="12" r="2" />
  </svg>
)

const LoadingSpinner = () => (
  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
  </svg>
)

interface BatchAnalysisProgress {
  analyzed: number
  total: number
  currentId?: string
}

interface DashboardLayoutProps {
  /** Opportunities to display */
  opportunities: Opportunity[]
  /** Total count for header */
  totalCount?: number
  /** Search query */
  searchQuery?: string
  /** Search handler */
  onSearch?: (query: string) => void
  /** Filter state */
  filters: SearchFilters
  /** Filter change handler */
  onFiltersChange: (filters: SearchFilters) => void
  /** Loading state */
  loading?: boolean
  /** Loading more state (for infinite scroll) */
  loadingMore?: boolean
  /** Whether there are more results to load */
  hasMore?: boolean
  /** Load more handler (for infinite scroll) */
  onLoadMore?: () => void
  /** Currently selected opportunity */
  selectedOpportunity?: Opportunity | null
  /** Selection handler */
  onSelectOpportunity?: (opp: Opportunity) => void
  /** Close detail panel handler */
  onCloseOpportunity?: () => void
  /** Current nav selection */
  activeNav?: string
  /** Nav change handler */
  onNavChange?: (nav: string) => void
  /** Batch analysis handler */
  onBatchAnalyze?: () => void
  /** Batch analysis progress */
  batchProgress?: BatchAnalysisProgress | null
  /** Whether batch analysis is running */
  isAnalyzing?: boolean
  /** Count of recommended (high-fit) opportunities */
  forYouCount?: number
  className?: string
}

/**
 * DashboardLayout - Full page layout with sidebar, header, and results
 *
 * Layout:
 * ┌──────────────────────────────────────────────────────────┐
 * │ [Logo]       [SearchInput.................] [Avatar]     │
 * ├─────┬────────────────────────────────────────────────────┤
 * │ Nav │  Results (count)                    [Filters btn]  │
 * │     │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
 * │     │  │ Card        │ │ Card        │ │ Card        │   │
 * │     │  └─────────────┘ └─────────────┘ └─────────────┘   │
 * └─────┴────────────────────────────────────────────────────┘
 */
export function DashboardLayout({
  opportunities,
  totalCount,
  searchQuery = '',
  onSearch,
  filters,
  onFiltersChange,
  loading = false,
  loadingMore = false,
  hasMore = false,
  onLoadMore,
  selectedOpportunity,
  onSelectOpportunity,
  onCloseOpportunity,
  activeNav = 'all',
  onNavChange,
  onBatchAnalyze,
  batchProgress,
  isAnalyzing = false,
  forYouCount,
  className,
}: DashboardLayoutProps) {
  const [showFilters, setShowFilters] = useState(false)
  const [localSearch, setLocalSearch] = useState(searchQuery)

  const navItems = [
    { id: 'all', label: 'All Results', icon: <HomeIcon />, count: totalCount },
    { id: 'foryou', label: 'For You', icon: <SparkleIcon />, count: forYouCount },
    { id: 'grants', label: 'Grants', icon: <FolderIcon /> },
    { id: 'contracts', label: 'Contracts', icon: <FileIcon /> },
    { id: 'rfis', label: 'RFIs', icon: <RfiIcon /> },
    { id: 'saved', label: 'Saved', icon: <StarIcon /> },
  ]

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSearch?.(localSearch)
  }

  return (
    <div className={cn('min-h-screen bg-bg-base', className)}>
      {/* Header */}
      <header
        className={cn(
          'fixed top-0 left-0 right-0 z-40',
          'h-16',
          'bg-bg-surface',
          'border-b border-border-default',
          'px-6',
          'flex items-center gap-6'
        )}
      >
        {/* Logo */}
        <div className="flex-shrink-0">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-accent-cyan flex items-center justify-center">
              <span className="text-bg-base font-bold text-sm">A</span>
            </div>
            <span className="text-text-primary font-semibold text-sm">
              Ariston
            </span>
          </div>
        </div>

        {/* Search */}
        <form onSubmit={handleSearchSubmit}>
          <SearchInput
            value={localSearch}
            onChange={setLocalSearch}
            placeholder="Search grants, contracts, RFIs..."
          />
        </form>

        {/* Avatar - pushed to far right */}
        <div className="flex-shrink-0 ml-auto">
          <button
            className={cn(
              'w-10 h-10',
              'rounded-full',
              'bg-bg-card',
              'border border-border-default',
              'flex items-center justify-center',
              'text-text-secondary',
              'hover:text-text-primary',
              'hover:border-accent-cyan',
              'transition-colors'
            )}
          >
            <UserIcon />
          </button>
        </div>
      </header>

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed left-0 top-16 bottom-0 z-30',
          'w-52',
          'bg-bg-surface',
          'border-r border-border-default',
          'flex flex-col'
        )}
      >
        <nav className="space-y-1 p-4 flex-1">
          {navItems.map((item) => (
            <NavItem
              key={item.id}
              icon={item.icon}
              label={item.label}
              badge={item.count}
              selected={activeNav === item.id}
              onClick={() => onNavChange?.(item.id)}
            />
          ))}
        </nav>

        {/* Analyze All Button - Fixed at bottom of sidebar */}
        <div className="p-4 border-t border-border-default">
          <button
            onClick={onBatchAnalyze}
            disabled={isAnalyzing || opportunities.length === 0}
            className={cn(
              'w-full flex items-center gap-3 px-4 py-3 rounded-lg',
              'text-sm font-medium',
              'transition-all duration-200',
              isAnalyzing
                ? 'bg-accent-cyan/20 text-accent-cyan cursor-wait'
                : 'bg-bg-card hover:bg-accent-cyan/10 text-text-primary hover:text-accent-cyan',
              'border border-border-default hover:border-accent-cyan/50',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
          >
            {isAnalyzing ? <LoadingSpinner /> : <AnalyzeIcon />}
            <div className="flex-1 text-left">
              {isAnalyzing ? (
                <>
                  <div className="text-xs text-text-secondary">Analyzing...</div>
                  <div className="text-sm">
                    {batchProgress?.analyzed ?? 0}/{batchProgress?.total ?? 0}
                  </div>
                </>
              ) : (
                <>
                  <div className="text-xs text-text-secondary">AI Analysis</div>
                  <div className="text-sm">Analyze All ({opportunities.length})</div>
                </>
              )}
            </div>
          </button>

          {/* Progress bar */}
          {isAnalyzing && batchProgress && (
            <div className="mt-2">
              <div className="h-1 bg-bg-card rounded-full overflow-hidden">
                <div
                  className="h-full bg-accent-cyan transition-all duration-300"
                  style={{
                    width: `${(batchProgress.analyzed / batchProgress.total) * 100}%`
                  }}
                />
              </div>
            </div>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <main
        className={cn(
          'pt-16 pl-52',
          'min-h-screen'
        )}
      >
        <div className="p-6">
          {/* Results Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-xl font-semibold text-text-primary">
                Results
                {totalCount !== undefined && (
                  <span className="text-text-secondary font-normal ml-2">
                    ({totalCount.toLocaleString()} opportunities)
                  </span>
                )}
              </h1>
            </div>
            <Button
              variant="secondary"
              icon={<FilterIcon />}
              onClick={() => setShowFilters(!showFilters)}
            >
              Filters
            </Button>
          </div>

          {/* Content Area with optional filter sidebar */}
          <div className="flex gap-6">
            {/* Results Grid */}
            <div className="flex-1">
              <SearchResultsGrid
                opportunities={opportunities}
                selectedId={selectedOpportunity?.opportunity_id}
                onSelect={onSelectOpportunity}
                loading={loading}
                loadingMore={loadingMore}
                hasMore={hasMore}
                onLoadMore={onLoadMore}
              />
            </div>

            {/* Filter Panel (collapsible) */}
            {showFilters && (
              <div className="w-72 flex-shrink-0">
                <FilterPanel
                  filters={filters}
                  onChange={onFiltersChange}
                  onClose={() => setShowFilters(false)}
                />
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Detail Panel Overlay */}
      {selectedOpportunity && (
        <>
          {/* Dark overlay */}
          <div
            className={cn(
              'fixed inset-0 z-40',
              'bg-black/50',
              'animate-fade-in'
            )}
            onClick={onCloseOpportunity}
          />

          {/* Detail Panel */}
          <OpportunityDetail
            opportunity={selectedOpportunity}
            onClose={() => onCloseOpportunity?.()}
          />
        </>
      )}
    </div>
  )
}

export default DashboardLayout
