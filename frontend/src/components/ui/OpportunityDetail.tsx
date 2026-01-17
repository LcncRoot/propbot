import { cn } from '@/lib/utils'
import { Opportunity, getOpportunityStatus, getOpportunityType, formatFunding, formatDeadline } from '@/types/opportunity'
import { Button } from './Button'

interface OpportunityDetailProps {
  opportunity: Opportunity
  onClose: () => void
  className?: string
}

// Close icon
const CloseIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="6" x2="6" y2="18" />
    <line x1="6" y1="6" x2="18" y2="18" />
  </svg>
)

// External link icon
const ExternalLinkIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
    <polyline points="15 3 21 3 21 9" />
    <line x1="10" y1="14" x2="21" y2="3" />
  </svg>
)

/**
 * OpportunityDetail - Slide-out panel showing full opportunity details
 */
export function OpportunityDetail({
  opportunity,
  onClose,
  className,
}: OpportunityDetailProps) {
  const status = getOpportunityStatus(opportunity.deadline)
  const type = getOpportunityType(opportunity)
  const sourceName = opportunity.source === 'grants.gov' ? 'Grants.gov' : 'SAM.gov'

  // Status badge colors
  const statusColors = {
    open: 'bg-success-green/20 text-success-green',
    closing_soon: 'bg-warning-amber/20 text-warning-amber',
    closed: 'bg-text-secondary/20 text-text-secondary',
  }

  // Type badge colors (keys match getOpportunityType output)
  const typeColors = {
    grant: 'bg-accent-teal/20 text-accent-teal',
    contract: 'bg-accent-cyan/20 text-accent-cyan',
    rfi: 'bg-warning-amber/20 text-warning-amber',
  }

  // Type labels for display
  const typeLabels = {
    grant: 'Grant',
    contract: 'Contract',
    rfi: 'RFI',
  }

  const statusLabels = {
    open: 'Open',
    closing_soon: 'Closing Soon',
    closed: 'Closed',
  }

  return (
    <div
      className={cn(
        // Panel container
        'fixed top-0 right-0 bottom-0',
        'w-[40vw] min-w-[400px] max-w-[600px]',
        'bg-bg-surface',
        'border-l border-border-default',
        'shadow-2xl',
        'z-50',
        // Flex layout
        'flex flex-col',
        // Animation
        'animate-slide-in-right',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border-default">
        <div className="flex items-center gap-2">
          {/* Type badge */}
          <span className={cn(
            'px-2 py-0.5 rounded text-xs font-medium',
            typeColors[type]
          )}>
            {typeLabels[type]}
          </span>
          {/* Status badge */}
          <span className={cn(
            'px-2 py-0.5 rounded text-xs font-medium',
            statusColors[status]
          )}>
            {statusLabels[status]}
          </span>
        </div>
        {/* Close button */}
        <button
          onClick={onClose}
          className={cn(
            'p-2 rounded-lg',
            'text-text-secondary hover:text-text-primary',
            'hover:bg-bg-card',
            'transition-colors'
          )}
        >
          <CloseIcon />
        </button>
      </div>

      {/* Scrollable content */}
      <div className="flex-1 overflow-y-auto p-6">
        {/* Title */}
        <h2 className="text-xl font-semibold text-text-primary leading-tight mb-2">
          {opportunity.title}
        </h2>

        {/* Agency */}
        <p className="text-sm text-text-secondary mb-6">
          {opportunity.agency}
        </p>

        {/* Divider */}
        <div className="border-t border-border-default mb-6" />

        {/* Description */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-text-secondary uppercase tracking-wide mb-3">
            Description
          </h3>
          <p className="text-sm text-text-primary leading-relaxed whitespace-pre-wrap">
            {opportunity.description || 'No description available.'}
          </p>
        </div>

        {/* Divider */}
        <div className="border-t border-border-default mb-6" />

        {/* Details section */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium text-text-secondary uppercase tracking-wide mb-3">
            Details
          </h3>

          {/* Funding amount */}
          {opportunity.funding_amount && (
            <DetailRow label="Funding Amount" value={formatFunding(opportunity.funding_amount)} />
          )}

          {/* Deadline */}
          <DetailRow
            label="Deadline"
            value={opportunity.deadline ? formatDeadline(opportunity.deadline) : 'Not specified'}
          />

          {/* Source */}
          <DetailRow label="Source" value={sourceName} />

          {/* NAICS code */}
          {opportunity.naics_code && (
            <DetailRow label="NAICS Code" value={opportunity.naics_code} />
          )}

          {/* Opportunity ID */}
          <DetailRow label="Opportunity ID" value={opportunity.opportunity_id} />
        </div>
      </div>

      {/* Footer with CTA */}
      <div className="p-4 border-t border-border-default">
        <Button
          variant="primary"
          fullWidth
          icon={<ExternalLinkIcon />}
          onClick={() => {
            if (opportunity.url) {
              window.open(opportunity.url, '_blank', 'noopener,noreferrer')
            }
          }}
        >
          View on {sourceName}
        </Button>
      </div>
    </div>
  )
}

// Helper component for detail rows
function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between items-start">
      <span className="text-sm text-text-secondary">{label}</span>
      <span className="text-sm text-text-primary text-right ml-4">{value}</span>
    </div>
  )
}

export default OpportunityDetail
