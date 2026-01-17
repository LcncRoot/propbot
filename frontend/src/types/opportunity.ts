/**
 * Opportunity types for PropBot
 */

export type OpportunitySource = 'grants.gov' | 'sam.gov'

export type OpportunityType = 'grant' | 'contract' | 'rfi'

export type OpportunityStatus = 'open' | 'closing_soon' | 'closed'

export interface Opportunity {
  id: number
  opportunity_id: string
  source: OpportunitySource
  title: string
  description?: string
  agency: string
  deadline?: string
  funding_amount?: number | null
  naics_code?: string | null
  cfda_numbers?: string | null
  url?: string
  notice_type?: string | null
  similarity_score?: number
  // Computed/aliased fields from API
  grant_url?: string
  link?: string
  response_deadline?: string
  cfda_number?: string[]
}

export interface SearchFilters {
  sources: {
    grants: boolean
    contracts: boolean
    rfis: boolean
  }
  status: {
    open: boolean
    closingSoon: boolean
    closed: boolean
  }
  fundingRange: {
    min: number | null
    max: number | null
  }
}

export interface SearchResults {
  grants: Opportunity[]
  contracts: Opportunity[]
  rfis: Opportunity[]
  search_mode: 'semantic' | 'keyword'
}

/**
 * Determine opportunity status based on deadline
 */
export function getOpportunityStatus(deadline?: string): OpportunityStatus {
  if (!deadline) return 'open'

  const deadlineDate = new Date(deadline)
  const now = new Date()
  const daysUntilDeadline = Math.ceil(
    (deadlineDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)
  )

  if (daysUntilDeadline < 0) return 'closed'
  if (daysUntilDeadline <= 7) return 'closing_soon'
  return 'open'
}

/**
 * Format funding amount for display
 */
export function formatFunding(amount?: number | null): string {
  if (!amount) return 'Not specified'

  if (amount >= 1_000_000) {
    return `$${(amount / 1_000_000).toFixed(1)}M`
  }
  if (amount >= 1_000) {
    return `$${(amount / 1_000).toFixed(0)}K`
  }
  return `$${amount.toLocaleString()}`
}

/**
 * Format deadline for display
 */
export function formatDeadline(deadline?: string): string {
  if (!deadline) return 'No deadline'

  const date = new Date(deadline)
  const now = new Date()
  const daysUntil = Math.ceil(
    (date.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)
  )

  if (daysUntil < 0) return 'Closed'
  if (daysUntil === 0) return 'Due today'
  if (daysUntil === 1) return 'Due tomorrow'
  if (daysUntil <= 7) return `${daysUntil} days left`

  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

/**
 * Get opportunity type from source and notice_type
 */
export function getOpportunityType(opp: Opportunity): OpportunityType {
  if (opp.source === 'grants.gov') return 'grant'
  if (opp.notice_type === 'Sources Sought' || opp.notice_type === 'Special Notice') {
    return 'rfi'
  }
  return 'contract'
}
