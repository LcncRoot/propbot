import { cn } from '@/lib/utils'
import {
  Opportunity,
  OpportunityStatus,
  getOpportunityStatus,
  formatFunding,
  formatDeadline,
  getOpportunityType,
} from '@/types/opportunity'

interface OpportunityCardProps {
  opportunity: Opportunity
  /** Whether this card is selected */
  selected?: boolean
  /** Click handler */
  onClick?: () => void
  className?: string
}

/**
 * OpportunityCard - Displays a grant, contract, or RFI opportunity
 *
 * Shows:
 * - Title (truncated to 2 lines)
 * - Agency
 * - Funding amount (if available)
 * - Deadline with status
 * - Source badge (grants.gov / sam.gov)
 * - Status badge (open / closing soon / closed)
 */
export function OpportunityCard({
  opportunity,
  selected = false,
  onClick,
  className,
}: OpportunityCardProps) {
  const status = getOpportunityStatus(opportunity.deadline)
  const type = getOpportunityType(opportunity)

  return (
    <article
      onClick={onClick}
      className={cn(
        // Layout
        'flex flex-col',
        'p-4',
        'min-h-[180px]',
        // Background & border
        'rounded-lg',
        'bg-bg-card',
        'border',
        selected ? 'border-accent-cyan' : 'border-border-default',
        // Shadow
        'card-highlight',
        selected && 'glow-cyan',
        // Transitions
        'transition-all duration-200',
        // Hover
        'cursor-pointer',
        'hover:bg-bg-card-hover',
        !selected && 'hover:border-border-default',
        // Custom
        className
      )}
    >
      {/* Header: Source & Status badges */}
      <div className="flex items-center justify-between mb-3">
        <SourceBadge source={opportunity.source} type={type} />
        <StatusBadge status={status} />
      </div>

      {/* Title */}
      <h3
        className={cn(
          'text-sm font-medium',
          'text-text-primary',
          'leading-tight',
          'truncate-2',
          'mb-2'
        )}
        title={opportunity.title}
      >
        {opportunity.title}
      </h3>

      {/* Agency */}
      <p
        className={cn(
          'text-xs',
          'text-text-secondary',
          'truncate',
          'mb-auto'
        )}
        title={opportunity.agency}
      >
        {opportunity.agency}
      </p>

      {/* Footer: Funding & Deadline */}
      <div className="flex items-center justify-between mt-3 pt-3 border-t border-border-default">
        <div className="flex flex-col">
          <span className="text-xs text-text-secondary">Funding</span>
          <span className="text-sm font-medium text-text-primary">
            {formatFunding(opportunity.funding_amount)}
          </span>
        </div>
        <div className="flex flex-col items-end">
          <span className="text-xs text-text-secondary">Deadline</span>
          <span
            className={cn(
              'text-sm font-medium',
              status === 'closing_soon' && 'text-warning-amber',
              status === 'closed' && 'text-text-secondary',
              status === 'open' && 'text-text-primary'
            )}
          >
            {formatDeadline(opportunity.deadline)}
          </span>
        </div>
      </div>
    </article>
  )
}

/**
 * Source badge component
 */
function SourceBadge({
  source,
  type,
}: {
  source: 'grants.gov' | 'sam.gov'
  type: 'grant' | 'contract' | 'rfi'
}) {
  const labels = {
    grant: 'Grant',
    contract: 'Contract',
    rfi: 'RFI',
  }

  const colors = {
    grant: 'bg-accent-teal/20 text-accent-teal',
    contract: 'bg-accent-cyan/20 text-accent-cyan',
    rfi: 'bg-warning-amber/20 text-warning-amber',
  }

  return (
    <span
      className={cn(
        'px-2 py-0.5',
        'text-xs font-medium',
        'rounded-full',
        colors[type]
      )}
    >
      {labels[type]}
    </span>
  )
}

/**
 * Status badge component
 */
function StatusBadge({ status }: { status: OpportunityStatus }) {
  const config = {
    open: {
      label: 'Open',
      classes: 'bg-success-green/20 text-success-green',
    },
    closing_soon: {
      label: 'Closing Soon',
      classes: 'bg-warning-amber/20 text-warning-amber',
    },
    closed: {
      label: 'Closed',
      classes: 'bg-error-red/20 text-error-red',
    },
  }

  const { label, classes } = config[status]

  return (
    <span
      className={cn(
        'px-2 py-0.5',
        'text-xs font-medium',
        'rounded-full',
        classes
      )}
    >
      {label}
    </span>
  )
}

export default OpportunityCard
