import { useState, useEffect } from 'react'
import { cn } from '@/lib/utils'
import { Opportunity, getOpportunityStatus, getOpportunityType, formatFunding, formatDeadline } from '@/types/opportunity'
import { Button } from './Button'

const API_BASE = 'http://localhost:8000'

interface Analysis {
  summary: string
  fit_score: number
  fit_reasoning: string
  key_requirements: string[]
  red_flags: string[]
  recommended_action: 'pursue' | 'research' | 'skip'
  model_used: string
  analyzed_at?: string
}

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

// AI/Analyze icon
const AnalyzeIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2a4 4 0 0 1 4 4c0 1.1-.45 2.1-1.17 2.83L12 12l-2.83-3.17A4 4 0 0 1 12 2z" />
    <path d="M12 12l2.83 3.17A4 4 0 1 1 12 22a4 4 0 0 1-2.83-6.83L12 12z" />
    <circle cx="12" cy="12" r="2" />
  </svg>
)

// Loading spinner
const LoadingSpinner = () => (
  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
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
  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const status = getOpportunityStatus(opportunity.deadline)
  const type = getOpportunityType(opportunity)
  const sourceName = opportunity.source === 'grants.gov' ? 'Grants.gov' : 'SAM.gov'

  // Check for existing analysis on mount
  useEffect(() => {
    const checkExistingAnalysis = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/analysis/${opportunity.opportunity_id}`)
        if (response.ok) {
          const data = await response.json()
          setAnalysis(data.analysis)
        }
      } catch {
        // No existing analysis, that's fine
      }
    }
    checkExistingAnalysis()
  }, [opportunity.opportunity_id])

  // Trigger analysis
  const handleAnalyze = async () => {
    setAnalyzing(true)
    setError(null)

    try {
      const response = await fetch(`${API_BASE}/api/analyze/${opportunity.opportunity_id}`, {
        method: 'POST',
      })

      if (!response.ok) {
        throw new Error('Analysis failed')
      }

      const data = await response.json()
      setAnalysis(data.analysis)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed')
    } finally {
      setAnalyzing(false)
    }
  }

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

        {/* Divider */}
        <div className="border-t border-border-default my-6" />

        {/* AI Analysis Section */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-text-secondary uppercase tracking-wide">
              AI Analysis
            </h3>
            {!analysis && !analyzing && (
              <Button
                variant="secondary"
                size="sm"
                icon={<AnalyzeIcon />}
                onClick={handleAnalyze}
              >
                Analyze
              </Button>
            )}
          </div>

          {analyzing && (
            <div className="flex items-center gap-3 p-4 rounded-lg bg-bg-card border border-border-default">
              <LoadingSpinner />
              <span className="text-sm text-text-secondary">Analyzing opportunity...</span>
            </div>
          )}

          {error && (
            <div className="p-4 rounded-lg bg-error-red/10 border border-error-red/30">
              <p className="text-sm text-error-red">{error}</p>
              <button
                onClick={handleAnalyze}
                className="text-sm text-accent-cyan hover:underline mt-2"
              >
                Try again
              </button>
            </div>
          )}

          {analysis && (
            <div className="space-y-4">
              {/* Fit Score */}
              <div className="flex items-center gap-4">
                <div className={cn(
                  'w-14 h-14 rounded-lg flex items-center justify-center text-xl font-bold',
                  analysis.fit_score >= 7 ? 'bg-success-green/20 text-success-green' :
                  analysis.fit_score >= 4 ? 'bg-warning-amber/20 text-warning-amber' :
                  'bg-error-red/20 text-error-red'
                )}>
                  {analysis.fit_score}/10
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-text-primary">Fit Score</p>
                  <p className="text-xs text-text-secondary">{analysis.fit_reasoning}</p>
                </div>
              </div>

              {/* Recommended Action */}
              <div className={cn(
                'px-3 py-2 rounded-lg text-sm font-medium inline-block',
                analysis.recommended_action === 'pursue' ? 'bg-success-green/20 text-success-green' :
                analysis.recommended_action === 'research' ? 'bg-warning-amber/20 text-warning-amber' :
                'bg-text-secondary/20 text-text-secondary'
              )}>
                Recommended: {analysis.recommended_action.toUpperCase()}
              </div>

              {/* Summary */}
              <div>
                <p className="text-xs text-text-secondary uppercase tracking-wide mb-1">Summary</p>
                <p className="text-sm text-text-primary">{analysis.summary}</p>
              </div>

              {/* Key Requirements */}
              {analysis.key_requirements.length > 0 && (
                <div>
                  <p className="text-xs text-text-secondary uppercase tracking-wide mb-2">Key Requirements</p>
                  <ul className="space-y-1">
                    {analysis.key_requirements.map((req, i) => (
                      <li key={i} className="text-sm text-text-primary flex items-start gap-2">
                        <span className="text-accent-cyan mt-1">•</span>
                        {req}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Red Flags */}
              {analysis.red_flags.length > 0 && (
                <div>
                  <p className="text-xs text-text-secondary uppercase tracking-wide mb-2">Red Flags</p>
                  <ul className="space-y-1">
                    {analysis.red_flags.map((flag, i) => (
                      <li key={i} className="text-sm text-warning-amber flex items-start gap-2">
                        <span className="mt-1">⚠</span>
                        {flag}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Re-analyze button */}
              <button
                onClick={handleAnalyze}
                disabled={analyzing}
                className="text-xs text-text-secondary hover:text-accent-cyan transition-colors"
              >
                Re-analyze
              </button>
            </div>
          )}

          {!analysis && !analyzing && !error && (
            <p className="text-sm text-text-secondary">
              Click "Analyze" to get AI-powered insights on this opportunity.
            </p>
          )}
        </div>
      </div>

      {/* Footer with CTA */}
      <div className="p-4 border-t border-border-default space-y-2">
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
