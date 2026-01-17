/**
 * UI Kit - PropBot Design System
 *
 * Phase 2: Layout Primitives (Surface, Card, Sidebar, SidebarItem)
 * Phase 3: Interactive Components (SearchInput, NavItem, Toggle, Button)
 *
 * Access via ?ui-kit query param
 */

import { useState } from 'react'
import {
  Card,
  SidebarItem,
  NavItem,
  SearchInput,
  Toggle,
  Button,
} from '@/components/ui'

// Icon components
const HomeIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
    <polyline points="9 22 9 12 15 12 15 22" />
  </svg>
)

const SearchIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8" />
    <path d="m21 21-4.35-4.35" />
  </svg>
)

const SettingsIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="3" />
    <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
  </svg>
)

const StarIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
  </svg>
)

const FolderIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
  </svg>
)

const FileIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
    <polyline points="14 2 14 8 20 8" />
  </svg>
)

const PlusIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="12" y1="5" x2="12" y2="19" />
    <line x1="5" y1="12" x2="19" y2="12" />
  </svg>
)

const FilterIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
  </svg>
)

export function UIKit() {
  const [selectedSidebarItem, setSelectedSidebarItem] = useState(0)
  const [selectedNavItem, setSelectedNavItem] = useState(0)
  const [searchValue, setSearchValue] = useState('')
  const [toggleStates, setToggleStates] = useState([true, false, true])

  const toggleState = (index: number) => {
    const newStates = [...toggleStates]
    newStates[index] = !newStates[index]
    setToggleStates(newStates)
  }

  return (
    <div className="min-h-screen bg-bg-base">
      {/* Demo Sidebar */}
      <div className="fixed left-0 top-0 h-screen w-16 bg-bg-base border-r border-border-default flex flex-col py-6 px-3 gap-2 z-50">
        <SidebarItem
          icon={<HomeIcon />}
          label="Home"
          selected={selectedSidebarItem === 0}
          onClick={() => setSelectedSidebarItem(0)}
        />
        <SidebarItem
          icon={<SearchIcon />}
          label="Search"
          selected={selectedSidebarItem === 1}
          onClick={() => setSelectedSidebarItem(1)}
        />
        <SidebarItem
          icon={<StarIcon />}
          label="Saved"
          selected={selectedSidebarItem === 2}
          onClick={() => setSelectedSidebarItem(2)}
        />
        <div className="flex-1" />
        <SidebarItem
          icon={<SettingsIcon />}
          label="Settings"
          selected={selectedSidebarItem === 3}
          onClick={() => setSelectedSidebarItem(3)}
        />
      </div>

      {/* Main Content */}
      <div className="ml-16 p-8">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <header className="mb-12">
            <h1 className="text-3xl font-semibold text-text-primary mb-2">
              PropBot UI Kit
            </h1>
            <p className="text-text-secondary">
              Component library for grant & contract search
            </p>
          </header>

          {/* Interactive Components */}
          <section className="mb-12">
            <h2 className="text-xl font-semibold text-text-primary mb-6">
              Interactive Components
            </h2>

            {/* SearchInput */}
            <div className="mb-10">
              <h3 className="text-sm font-medium text-text-secondary mb-4 uppercase tracking-wider">
                SearchInput
              </h3>
              <div className="flex gap-6 items-start">
                <div>
                  <SearchInput
                    value={searchValue}
                    onChange={setSearchValue}
                    placeholder="Search grants, contracts, RFIs..."
                  />
                  <p className="text-xs text-text-secondary mt-2">Default width</p>
                </div>
                <div className="flex-1 max-w-md">
                  <SearchInput
                    placeholder="Full width search..."
                    fullWidth
                  />
                  <p className="text-xs text-text-secondary mt-2">fullWidth=true</p>
                </div>
              </div>
              {searchValue && (
                <p className="text-sm text-text-secondary mt-4">
                  Searching for: <span className="text-accent-cyan">{searchValue}</span>
                </p>
              )}
            </div>

            {/* NavItem */}
            <div className="mb-10">
              <h3 className="text-sm font-medium text-text-secondary mb-4 uppercase tracking-wider">
                NavItem
              </h3>
              <div className="flex gap-8">
                <Card className="p-2 w-56">
                  <div className="flex flex-col gap-1">
                    <NavItem
                      icon={<HomeIcon />}
                      label="Dashboard"
                      selected={selectedNavItem === 0}
                      onClick={() => setSelectedNavItem(0)}
                    />
                    <NavItem
                      icon={<FolderIcon />}
                      label="Grants"
                      badge={12}
                      selected={selectedNavItem === 1}
                      onClick={() => setSelectedNavItem(1)}
                    />
                    <NavItem
                      icon={<FileIcon />}
                      label="Contracts"
                      badge={5}
                      selected={selectedNavItem === 2}
                      onClick={() => setSelectedNavItem(2)}
                    />
                    <NavItem
                      icon={<FilterIcon />}
                      label="RFIs"
                      badge={3}
                      selected={selectedNavItem === 3}
                      onClick={() => setSelectedNavItem(3)}
                    />
                    <NavItem
                      icon={<StarIcon />}
                      label="Saved"
                      selected={selectedNavItem === 4}
                      onClick={() => setSelectedNavItem(4)}
                    />
                  </div>
                </Card>
                <div className="flex-1">
                  <p className="text-text-secondary text-sm mb-4">States:</p>
                  <div className="flex flex-col gap-2 max-w-xs">
                    <NavItem icon={<HomeIcon />} label="Default" />
                    <NavItem icon={<SearchIcon />} label="Selected" selected />
                    <NavItem icon={<FolderIcon />} label="With badge" badge={8} />
                  </div>
                </div>
              </div>
            </div>

            {/* Toggle */}
            <div className="mb-10">
              <h3 className="text-sm font-medium text-text-secondary mb-4 uppercase tracking-wider">
                Toggle
              </h3>
              <div className="flex gap-8 items-start">
                <div className="flex flex-col gap-4">
                  <div className="flex items-center gap-3">
                    <Toggle
                      checked={toggleStates[0]}
                      onChange={() => toggleState(0)}
                    />
                    <span className="text-sm text-text-primary">Grants.gov</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Toggle
                      checked={toggleStates[1]}
                      onChange={() => toggleState(1)}
                    />
                    <span className="text-sm text-text-primary">SAM.gov Contracts</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Toggle
                      checked={toggleStates[2]}
                      onChange={() => toggleState(2)}
                    />
                    <span className="text-sm text-text-primary">RFIs / Sources Sought</span>
                  </div>
                </div>
                <div className="flex flex-col gap-4">
                  <p className="text-text-secondary text-sm">Sizes:</p>
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                      <Toggle size="sm" checked />
                      <span className="text-xs text-text-secondary">sm</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Toggle size="md" checked />
                      <span className="text-xs text-text-secondary">md</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 mt-2">
                    <Toggle disabled />
                    <span className="text-xs text-text-secondary">disabled</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Button */}
            <div className="mb-10">
              <h3 className="text-sm font-medium text-text-secondary mb-4 uppercase tracking-wider">
                Button
              </h3>
              <div className="space-y-6">
                <div>
                  <p className="text-text-secondary text-sm mb-3">Variants:</p>
                  <div className="flex gap-4 items-center">
                    <Button variant="primary">Primary</Button>
                    <Button variant="secondary">Secondary</Button>
                    <Button variant="ghost">Ghost</Button>
                  </div>
                </div>
                <div>
                  <p className="text-text-secondary text-sm mb-3">Sizes:</p>
                  <div className="flex gap-4 items-center">
                    <Button size="sm">Small</Button>
                    <Button size="md">Medium</Button>
                    <Button size="lg">Large</Button>
                  </div>
                </div>
                <div>
                  <p className="text-text-secondary text-sm mb-3">With icons:</p>
                  <div className="flex gap-4 items-center">
                    <Button variant="primary" icon={<PlusIcon />}>New Search</Button>
                    <Button variant="secondary" icon={<FilterIcon />}>Filters</Button>
                    <Button variant="ghost" icon={<StarIcon />}>Save</Button>
                  </div>
                </div>
                <div>
                  <p className="text-text-secondary text-sm mb-3">States:</p>
                  <div className="flex gap-4 items-center">
                    <Button variant="primary">Normal</Button>
                    <Button variant="primary" disabled>Disabled</Button>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Layout Primitives */}
          <section className="mb-12">
            <h2 className="text-xl font-semibold text-text-primary mb-6">
              Layout Primitives
            </h2>
            <div className="mb-8">
              <h3 className="text-sm font-medium text-text-secondary mb-4 uppercase tracking-wider">
                Card States
              </h3>
              <div className="grid grid-cols-3 gap-4">
                <Card className="p-6">
                  <p className="text-text-primary font-medium mb-1">Default</p>
                  <p className="text-text-secondary text-sm">Basic card</p>
                </Card>
                <Card hoverable className="p-6">
                  <p className="text-text-primary font-medium mb-1">Hoverable</p>
                  <p className="text-text-secondary text-sm">Hover me</p>
                </Card>
                <Card active className="p-6">
                  <p className="text-text-primary font-medium mb-1">Active</p>
                  <p className="text-text-secondary text-sm">Cyan glow</p>
                </Card>
              </div>
            </div>
          </section>

          {/* Color Tokens */}
          <section className="mb-12">
            <h2 className="text-xl font-semibold text-text-primary mb-6">
              Color Tokens
            </h2>
            <div className="grid grid-cols-2 gap-8">
              <div>
                <h3 className="text-sm font-medium text-text-secondary mb-4 uppercase tracking-wider">
                  Backgrounds
                </h3>
                <div className="flex gap-3 flex-wrap">
                  <ColorSwatch name="base" color="#0a1628" />
                  <ColorSwatch name="surface" color="#0f1d32" />
                  <ColorSwatch name="card" color="#162032" />
                  <ColorSwatch name="hover" color="#1a2840" />
                  <ColorSwatch name="selected" color="#1e3a5f" />
                </div>
              </div>
              <div>
                <h3 className="text-sm font-medium text-text-secondary mb-4 uppercase tracking-wider">
                  Accents
                </h3>
                <div className="flex gap-3 flex-wrap">
                  <ColorSwatch name="cyan" color="#22d3ee" />
                  <ColorSwatch name="teal" color="#14b8a6" />
                  <ColorSwatch name="green" color="#22c55e" />
                  <ColorSwatch name="amber" color="#f59e0b" />
                  <ColorSwatch name="red" color="#ef4444" />
                </div>
              </div>
            </div>
          </section>

          {/* Phase 4 Preview */}
          <section className="mb-12">
            <h2 className="text-xl font-semibold text-text-primary mb-6">
              Phase 4: PropBot Components
            </h2>
            <p className="text-text-secondary">
              Awaiting data structure for: OpportunityCard, SearchResultsGrid, FilterPanel, DashboardLayout
            </p>
          </section>
        </div>
      </div>
    </div>
  )
}

function ColorSwatch({ name, color }: { name: string; color: string }) {
  return (
    <div className="flex flex-col items-center">
      <div
        className="w-12 h-12 rounded-md border border-border-default"
        style={{ backgroundColor: color }}
      />
      <span className="text-xs text-text-secondary mt-1">{name}</span>
    </div>
  )
}

export default UIKit
