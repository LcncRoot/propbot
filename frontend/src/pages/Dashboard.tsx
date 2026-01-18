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

interface BatchAnalysisProgress {
  analyzed: number
  total: number
  currentId?: string
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

  // Batch analysis state
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [batchProgress, setBatchProgress] = useState<BatchAnalysisProgress | null>(null)

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

  // RFI notice types (matches backend definition)
  const RFI_NOTICE_TYPES = ['Sources Sought', 'Special Notice']

  const isRfi = (opp: Opportunity) => RFI_NOTICE_TYPES.includes(opp.notice_type || '')
  const isContract = (opp: Opportunity) => opp.source === 'sam.gov' && !isRfi(opp)
  const isGrant = (opp: Opportunity) => opp.source === 'grants.gov'

  // Filter opportunities based on current filters and nav
  const filteredOpportunities = opportunities.filter((opp) => {
    // Nav filter
    if (activeNav === 'grants' && !isGrant(opp)) return false
    if (activeNav === 'contracts' && !isContract(opp)) return false
    if (activeNav === 'rfis' && !isRfi(opp)) return false

    // Source filter (for "all" view)
    if (isGrant(opp) && !filters.sources.grants) return false
    if (isContract(opp) && !filters.sources.contracts) return false
    if (isRfi(opp) && !filters.sources.rfis) return false

    return true
  })

  // Use total from stats when not searching, otherwise use filtered count
  const displayCount = searchQuery.trim()
    ? filteredOpportunities.length
    : (totalCount ?? filteredOpportunities.length)

  // Batch analysis handler
  const handleBatchAnalyze = useCallback(async () => {
    if (isAnalyzing || filteredOpportunities.length === 0) return

    setIsAnalyzing(true)
    setBatchProgress({ analyzed: 0, total: filteredOpportunities.length })

    try {
      const opportunityIds = filteredOpportunities.map(opp => opp.opportunity_id)

      const response = await fetch(`${API_BASE}/api/analyze/batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ opportunity_ids: opportunityIds }),
      })

      if (!response.ok) {
        throw new Error('Batch analysis failed')
      }

      // Read SSE stream
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('No response body')
      }

      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })

        // Parse SSE events from buffer
        const lines = buffer.split('\n\n')
        buffer = lines.pop() || '' // Keep incomplete event in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6))

            if (data.type === 'progress') {
              setBatchProgress({
                analyzed: data.analyzed,
                total: data.total,
                currentId: data.current_id,
              })
            } else if (data.type === 'complete') {
              console.log('Batch analysis complete:', data)
              // Could store results or trigger a refresh here
            }
          }
        }
      }
    } catch (error) {
      console.error('Batch analysis error:', error)
    } finally {
      setIsAnalyzing(false)
      setBatchProgress(null)
    }
  }, [filteredOpportunities, isAnalyzing])

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
      onBatchAnalyze={handleBatchAnalyze}
      batchProgress={batchProgress}
      isAnalyzing={isAnalyzing}
    />
  )
}

export default Dashboard
