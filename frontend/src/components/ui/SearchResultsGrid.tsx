import { cn } from '@/lib/utils'
import { Opportunity } from '@/types/opportunity'
import { OpportunityCard } from './OpportunityCard'

interface SearchResultsGridProps {
  /** Array of opportunities to display */
  opportunities: Opportunity[]
  /** Currently selected opportunity ID */
  selectedId?: string | null
  /** Callback when an opportunity is clicked */
  onSelect?: (opportunity: Opportunity) => void
  /** Loading state */
  loading?: boolean
  /** Empty state message */
  emptyMessage?: string
  className?: string
}

/**
 * SearchResultsGrid - Responsive grid of OpportunityCards
 *
 * Responsive columns:
 * - Desktop (xl+): 3 columns
 * - Tablet (md-xl): 2 columns
 * - Mobile (<md): 1 column
 */
export function SearchResultsGrid({
  opportunities,
  selectedId,
  onSelect,
  loading = false,
  emptyMessage = 'No opportunities found. Try adjusting your search or filters.',
  className,
}: SearchResultsGridProps) {
  // Loading state
  if (loading) {
    return (
      <div
        className={cn(
          'grid gap-4',
          'grid-cols-1 md:grid-cols-2 xl:grid-cols-3',
          className
        )}
      >
        {Array.from({ length: 6 }).map((_, i) => (
          <LoadingCard key={i} />
        ))}
      </div>
    )
  }

  // Empty state
  if (opportunities.length === 0) {
    return (
      <div
        className={cn(
          'flex flex-col items-center justify-center',
          'py-16 px-8',
          'text-center',
          className
        )}
      >
        <EmptyIcon />
        <p className="text-text-secondary mt-4 max-w-md">
          {emptyMessage}
        </p>
      </div>
    )
  }

  // Results grid
  return (
    <div
      className={cn(
        'grid gap-4',
        'grid-cols-1 md:grid-cols-2 xl:grid-cols-3',
        className
      )}
    >
      {opportunities.map((opp) => (
        <OpportunityCard
          key={opp.opportunity_id}
          opportunity={opp}
          selected={selectedId === opp.opportunity_id}
          onClick={() => onSelect?.(opp)}
        />
      ))}
    </div>
  )
}

/**
 * Loading skeleton card
 */
function LoadingCard() {
  return (
    <div
      className={cn(
        'flex flex-col',
        'p-4',
        'min-h-[180px]',
        'rounded-lg',
        'bg-bg-card',
        'border border-border-default',
        'animate-pulse'
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="h-5 w-16 bg-bg-card-hover rounded-full" />
        <div className="h-5 w-20 bg-bg-card-hover rounded-full" />
      </div>

      {/* Title */}
      <div className="h-4 w-full bg-bg-card-hover rounded mb-2" />
      <div className="h-4 w-3/4 bg-bg-card-hover rounded mb-2" />

      {/* Agency */}
      <div className="h-3 w-1/2 bg-bg-card-hover rounded mb-auto" />

      {/* Footer */}
      <div className="flex items-center justify-between mt-3 pt-3 border-t border-border-default">
        <div className="flex flex-col gap-1">
          <div className="h-3 w-12 bg-bg-card-hover rounded" />
          <div className="h-4 w-16 bg-bg-card-hover rounded" />
        </div>
        <div className="flex flex-col items-end gap-1">
          <div className="h-3 w-14 bg-bg-card-hover rounded" />
          <div className="h-4 w-20 bg-bg-card-hover rounded" />
        </div>
      </div>
    </div>
  )
}

/**
 * Empty state icon
 */
function EmptyIcon() {
  return (
    <svg
      width="64"
      height="64"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="text-text-secondary opacity-50"
    >
      <circle cx="11" cy="11" r="8" />
      <path d="m21 21-4.35-4.35" />
      <path d="M8 11h6" />
    </svg>
  )
}

export default SearchResultsGrid
