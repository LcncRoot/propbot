/**
 * Dashboard Page
 *
 * Shows DashboardLayout with real data from backend API.
 * Access via ?dashboard query param
 */

import { useState, useEffect, useCallback } from 'react'
import { DashboardLayout } from '@/components/ui'
import { Opportunity, SearchFilters } from '@/types/opportunity'

const API_BASE = 'http://localhost:8000'

interface ApiSearchResponse {
  grants: Opportunity[]
  contracts: Opportunity[]
  rfis: Opportunity[]
  search_mode: string
}

interface ApiListResponse {
  opportunities: Opportunity[]
  count: number
}

export function Dashboard() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [activeNav, setActiveNav] = useState('all')
  const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null)
  const [filters, setFilters] = useState<SearchFilters>({
    sources: { grants: true, contracts: true, rfis: true },
    status: { open: true, closingSoon: true, closed: false },
    fundingRange: { min: null, max: null },
  })

  // Fetch all opportunities on initial load
  useEffect(() => {
    const fetchInitial = async () => {
      setLoading(true)
      try {
        const response = await fetch(`${API_BASE}/api/opportunities?limit=100`)
        const data: ApiListResponse = await response.json()
        setOpportunities(data.opportunities)
      } catch (error) {
        console.error('Failed to fetch opportunities:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchInitial()
  }, [])

  // Search handler
  const handleSearch = useCallback(async (query: string) => {
    setSearchQuery(query)

    if (!query.trim()) {
      // If search cleared, fetch all opportunities
      setLoading(true)
      try {
        const response = await fetch(`${API_BASE}/api/opportunities?limit=100`)
        const data: ApiListResponse = await response.json()
        setOpportunities(data.opportunities)
      } catch (error) {
        console.error('Failed to fetch opportunities:', error)
      } finally {
        setLoading(false)
      }
      return
    }

    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/api/search?query=${encodeURIComponent(query)}&limit=50`)
      const data: ApiSearchResponse = await response.json()

      // Combine all results into a single array
      const combined: Opportunity[] = [
        ...data.grants.map(g => ({ ...g, source: 'grants.gov' as const })),
        ...data.contracts.map(c => ({ ...c, source: 'sam.gov' as const })),
        ...data.rfis.map(r => ({ ...r, source: 'sam.gov' as const })),
      ]

      setOpportunities(combined)
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      setLoading(false)
    }
  }, [])

  // Filter opportunities based on current filters and nav
  const filteredOpportunities = opportunities.filter((opp) => {
    // Nav filter
    if (activeNav === 'grants' && opp.source !== 'grants.gov') return false
    if (activeNav === 'contracts' && (opp.source !== 'sam.gov' || opp.notice_type)) return false
    if (activeNav === 'rfis' && !opp.notice_type) return false

    // Source filter
    if (opp.source === 'grants.gov' && !filters.sources.grants) return false
    if (opp.source === 'sam.gov' && !opp.notice_type && !filters.sources.contracts) return false
    if (opp.notice_type && !filters.sources.rfis) return false

    return true
  })

  return (
    <DashboardLayout
      opportunities={filteredOpportunities}
      totalCount={filteredOpportunities.length}
      searchQuery={searchQuery}
      onSearch={handleSearch}
      filters={filters}
      onFiltersChange={setFilters}
      activeNav={activeNav}
      onNavChange={setActiveNav}
      selectedOpportunity={selectedOpportunity}
      onSelectOpportunity={setSelectedOpportunity}
      onCloseOpportunity={() => setSelectedOpportunity(null)}
      loading={loading}
    />
  )
}

export default Dashboard
