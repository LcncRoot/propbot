import { cn } from '@/lib/utils'
import { SearchFilters } from '@/types/opportunity'
import { Toggle } from './Toggle'
import { Button } from './Button'

interface FilterPanelProps {
  /** Current filter state */
  filters: SearchFilters
  /** Callback when filters change */
  onChange: (filters: SearchFilters) => void
  /** Whether the panel is open */
  isOpen?: boolean
  /** Callback to close the panel */
  onClose?: () => void
  className?: string
}

/**
 * FilterPanel - Filter controls for opportunity search
 *
 * Filters:
 * - Source: Grants.gov, SAM.gov Contracts, RFIs
 * - Status: Open, Closing Soon, Closed
 * - Funding Range: Min/Max inputs
 */
export function FilterPanel({
  filters,
  onChange,
  isOpen = true,
  onClose,
  className,
}: FilterPanelProps) {
  const updateSource = (key: keyof typeof filters.sources) => {
    onChange({
      ...filters,
      sources: {
        ...filters.sources,
        [key]: !filters.sources[key],
      },
    })
  }

  const updateStatus = (key: keyof typeof filters.status) => {
    onChange({
      ...filters,
      status: {
        ...filters.status,
        [key]: !filters.status[key],
      },
    })
  }

  const resetFilters = () => {
    onChange({
      sources: { grants: true, contracts: true, rfis: true },
      status: { open: true, closingSoon: true, closed: false },
      fundingRange: { min: null, max: null },
    })
  }

  if (!isOpen) return null

  return (
    <div
      className={cn(
        'bg-bg-card',
        'border border-border-default',
        'rounded-lg',
        'p-4',
        'space-y-6',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-text-primary uppercase tracking-wider">
          Filters
        </h3>
        <Button variant="ghost" size="sm" onClick={resetFilters}>
          Reset
        </Button>
      </div>

      {/* Source Filters */}
      <div>
        <h4 className="text-xs font-medium text-text-secondary mb-3 uppercase tracking-wider">
          Source
        </h4>
        <div className="space-y-3">
          <FilterToggle
            label="Grants.gov"
            checked={filters.sources.grants}
            onChange={() => updateSource('grants')}
            color="teal"
          />
          <FilterToggle
            label="SAM.gov Contracts"
            checked={filters.sources.contracts}
            onChange={() => updateSource('contracts')}
            color="cyan"
          />
          <FilterToggle
            label="RFIs / Sources Sought"
            checked={filters.sources.rfis}
            onChange={() => updateSource('rfis')}
            color="amber"
          />
        </div>
      </div>

      {/* Status Filters */}
      <div>
        <h4 className="text-xs font-medium text-text-secondary mb-3 uppercase tracking-wider">
          Status
        </h4>
        <div className="space-y-3">
          <FilterToggle
            label="Open"
            checked={filters.status.open}
            onChange={() => updateStatus('open')}
            color="green"
          />
          <FilterToggle
            label="Closing Soon"
            checked={filters.status.closingSoon}
            onChange={() => updateStatus('closingSoon')}
            color="amber"
          />
          <FilterToggle
            label="Closed"
            checked={filters.status.closed}
            onChange={() => updateStatus('closed')}
            color="red"
          />
        </div>
      </div>

      {/* Funding Range */}
      <div>
        <h4 className="text-xs font-medium text-text-secondary mb-3 uppercase tracking-wider">
          Funding Range
        </h4>
        <div className="flex gap-3">
          <div className="flex-1">
            <label className="text-xs text-text-secondary mb-1 block">Min</label>
            <input
              type="number"
              placeholder="$0"
              value={filters.fundingRange.min ?? ''}
              onChange={(e) =>
                onChange({
                  ...filters,
                  fundingRange: {
                    ...filters.fundingRange,
                    min: e.target.value ? Number(e.target.value) : null,
                  },
                })
              }
              className={cn(
                'w-full',
                'px-3 py-2',
                'text-sm',
                'bg-bg-base',
                'border border-border-default',
                'rounded-md',
                'text-text-primary',
                'placeholder:text-text-secondary',
                'focus:outline-none',
                'focus:border-accent-cyan'
              )}
            />
          </div>
          <div className="flex-1">
            <label className="text-xs text-text-secondary mb-1 block">Max</label>
            <input
              type="number"
              placeholder="No limit"
              value={filters.fundingRange.max ?? ''}
              onChange={(e) =>
                onChange({
                  ...filters,
                  fundingRange: {
                    ...filters.fundingRange,
                    max: e.target.value ? Number(e.target.value) : null,
                  },
                })
              }
              className={cn(
                'w-full',
                'px-3 py-2',
                'text-sm',
                'bg-bg-base',
                'border border-border-default',
                'rounded-md',
                'text-text-primary',
                'placeholder:text-text-secondary',
                'focus:outline-none',
                'focus:border-accent-cyan'
              )}
            />
          </div>
        </div>
      </div>

      {/* Apply button (mobile) */}
      {onClose && (
        <Button variant="primary" fullWidth onClick={onClose}>
          Apply Filters
        </Button>
      )}
    </div>
  )
}

/**
 * Filter toggle with colored indicator
 */
function FilterToggle({
  label,
  checked,
  onChange,
  color,
}: {
  label: string
  checked: boolean
  onChange: () => void
  color: 'teal' | 'cyan' | 'amber' | 'green' | 'red'
}) {
  const colorClasses = {
    teal: 'bg-accent-teal',
    cyan: 'bg-accent-cyan',
    amber: 'bg-warning-amber',
    green: 'bg-success-green',
    red: 'bg-error-red',
  }

  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        <span
          className={cn(
            'w-2 h-2 rounded-full',
            checked ? colorClasses[color] : 'bg-border-default'
          )}
        />
        <span className="text-sm text-text-primary">{label}</span>
      </div>
      <Toggle checked={checked} onChange={onChange} size="sm" />
    </div>
  )
}

export default FilterPanel
