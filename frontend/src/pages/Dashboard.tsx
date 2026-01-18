/**
 * Dashboard Page
 *
 * Shows DashboardLayout with real data from backend API.
 * Implements infinite scroll pagination for large datasets.
 * Access via ?dashboard query param
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { DashboardLayout } from '@/components/ui'
import { Opportunity, SearchFilters } from '@/types/opportunity'

const API_BASE = 'http://localhost:8000'
const PAGE_SIZE = 50

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
  const [loadingMore, setLoadingMore] = useState(false)
  const [hasMore, setHasMore] = useState(true)
  const [totalCount, setTotalCount] = useState<number | undefined>(undefined)
  const offsetRef = useRef(0)
  const [searchQuery, setSearchQuery] = useState('')
  const [activeNav, setActiveNav] = useState('all')
  const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null)
  const [filters, setFilters] = useState<SearchFilters>({
    sources: { grants: true, contracts: true, rfis: true },
    status: { open: true, closingSoon: true, closed: false },
    fundingRange: { min: null, max: null },
  })

  // Fetch total count on mount
  useEffect(() => {
    const fetchCount = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/stats`)
        const data = await response.json()
        setTotalCount(data.total)
      } catch (error) {
        console.error('Failed to fetch stats:', error)
      }
    }
    fetchCount()
  }, [])

  // Fetch initial opportunities on mount
  useEffect(() => {
    const fetchInitial = async () => {
      setLoading(true)
      offsetRef.current = 0
      try {
        const response = await fetch(`${API_BASE}/api/opportunities?limit=${PAGE_SIZE}&offset=0`)
        const data: ApiListResponse = await response.json()
        setOpportunities(data.opportunities)
        offsetRef.current = data.opportunities.length
        setHasMore(data.opportunities.length === PAGE_SIZE)
      } catch (error) {
        console.error('Failed to fetch opportunities:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchInitial()
  }, [])

  // Load more opportunities (for infinite scroll)
  const loadMore = useCallback(async () => {
    if (loadingMore || !hasMore || searchQuery.trim()) return

    setLoadingMore(true)
    try {
      const response = await fetch(
        `${API_BASE}/api/opportunities?limit=${PAGE_SIZE}&offset=${offsetRef.current}`
      )
      const data: ApiListResponse = await response.json()

      if (data.opportunities.length > 0) {
        setOpportunities(prev => [...prev, ...data.opportunities])
        offsetRef.current += data.opportunities.length
        setHasMore(data.opportunities.length === PAGE_SIZE)
      } else {
        setHasMore(false)
      }
    } catch (error) {
      console.error('Failed to load more opportunities:', error)
    } finally {
      setLoadingMore(false)
    }
  }, [loadingMore, hasMore, searchQuery])

  // Search handler
  const handleSearch = useCallback(async (query: string) => {
    setSearchQuery(query)

    if (!query.trim()) {
      // If search cleared, reset to paginated list
      setLoading(true)
      offsetRef.current = 0
      try {
        const response = await fetch(`${API_BASE}/api/opportunities?limit=${PAGE_SIZE}&offset=0`)
        const data: ApiListResponse = await response.json()
        setOpportunities(data.opportunities)
        offsetRef.current = data.opportunities.length
        setHasMore(data.opportunities.length === PAGE_SIZE)
      } catch (error) {
        console.error('Failed to fetch opportunities:', error)
      } finally {
        setLoading(false)
      }
      return
    }

    // When searching, load all results (no pagination for search)
    setLoading(true)
    setHasMore(false) // Disable infinite scroll during search
    try {
      const response = await fetch(`${API_BASE}/api/search?query=${encodeURIComponent(query)}&limit=100`)
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

  // Use total from stats when not searching, otherwise use filtered count
  const displayCount = searchQuery.trim()
    ? filteredOpportunities.length
    : (totalCount ?? filteredOpportunities.length)

  return (
    <DashboardLayout
      opportunities={filteredOpportunities}
      totalCount={displayCount}
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
      loadingMore={loadingMore}
      hasMore={hasMore && !searchQuery.trim()}
      onLoadMore={loadMore}
    />
  )
}

export default Dashboard
