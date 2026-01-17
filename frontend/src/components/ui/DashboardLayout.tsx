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
  selectedOpportunity,
  onSelectOpportunity,
  onCloseOpportunity,
  activeNav = 'all',
  onNavChange,
  className,
}: DashboardLayoutProps) {
  const [showFilters, setShowFilters] = useState(false)
  const [localSearch, setLocalSearch] = useState(searchQuery)

  const navItems = [
    { id: 'all', label: 'All Results', icon: <HomeIcon />, count: totalCount },
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
          'p-4',
          'overflow-y-auto'
        )}
      >
        <nav className="space-y-1">
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
