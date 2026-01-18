import { useEffect, useRef, useCallback } from 'react'
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
  /** Loading state (initial load) */
  loading?: boolean
  /** Loading more state (infinite scroll) */
  loadingMore?: boolean
  /** Whether there are more results to load */
  hasMore?: boolean
  /** Callback to load more results */
  onLoadMore?: () => void
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
  loadingMore = false,
  hasMore = false,
  onLoadMore,
  emptyMessage = 'No opportunities found. Try adjusting your search or filters.',
  className,
}: SearchResultsGridProps) {
  const loadMoreRef = useRef<HTMLDivElement>(null)

  // IntersectionObserver for infinite scroll
  const handleObserver = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const target = entries[0]
      if (target.isIntersecting && hasMore && !loadingMore && onLoadMore) {
        onLoadMore()
      }
    },
    [hasMore, loadingMore, onLoadMore]
  )

  useEffect(() => {
    const observer = new IntersectionObserver(handleObserver, {
      root: null,
      rootMargin: '200px', // Trigger 200px before reaching the end
      threshold: 0,
    })

    if (loadMoreRef.current) {
      observer.observe(loadMoreRef.current)
    }

    return () => observer.disconnect()
  }, [handleObserver])

  // Loading state (initial load)
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

  // Results grid with infinite scroll sentinel
  return (
    <div className={className}>
      <div
        className={cn(
          'grid gap-4',
          'grid-cols-1 md:grid-cols-2 xl:grid-cols-3'
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

      {/* Infinite scroll sentinel and loading indicator */}
      <div ref={loadMoreRef} className="py-8 flex justify-center">
        {loadingMore && (
          <div className="flex items-center gap-3 text-text-secondary">
            <LoadingSpinner />
            <span>Loading more opportunities...</span>
          </div>
        )}
        {!hasMore && opportunities.length > 0 && (
          <p className="text-text-secondary text-sm">
            All {opportunities.length} opportunities loaded
          </p>
        )}
      </div>
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

/**
 * Loading spinner for infinite scroll
 */
function LoadingSpinner() {
  return (
    <svg
      className="animate-spin h-5 w-5"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  )
}

export default SearchResultsGrid
