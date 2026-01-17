import { cn } from '@/lib/utils'

interface SearchInputProps {
  /** Current value */
  value?: string
  /** Change handler */
  onChange?: (value: string) => void
  /** Placeholder text */
  placeholder?: string
  /** Full width */
  fullWidth?: boolean
  className?: string
}

// Search icon component
const SearchIcon = () => (
  <svg
    width="18"
    height="18"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.5"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <circle cx="11" cy="11" r="8" />
    <path d="m21 21-4.35-4.35" />
  </svg>
)

/**
 * SearchInput - Rounded input with search icon
 *
 * Features:
 * - Search icon on left
 * - Rounded pill shape
 * - Focus state with cyan ring
 * - Dark theme styling
 */
export function SearchInput({
  value,
  onChange,
  placeholder = 'Search...',
  fullWidth = false,
  className,
}: SearchInputProps) {
  return (
    <label
      className={cn(
        // Fixed width - standard search bar size
        'w-[360px]',
        'flex-shrink-0',
        // Layout - use label as flex container for proper click handling
        'flex items-center gap-3',
        'cursor-text',
        // Shape
        'rounded-full',
        // Padding
        'pl-4 pr-4 py-2.5',
        // Overflow - keep text inside
        'overflow-hidden',
        // Background & border
        'bg-bg-card',
        'border border-border-default',
        // Transitions
        'transition-colors duration-200',
        // Focus-within state (when input inside is focused)
        'focus-within:outline-none',
        'focus-within:border-accent-cyan',
        'focus-within:ring-2',
        'focus-within:ring-accent-cyan/20',
        // Hover state
        'hover:bg-bg-card-hover',
        // Custom classes
        className
      )}
    >
      {/* Search icon */}
      <span className="text-text-secondary flex-shrink-0">
        <SearchIcon />
      </span>

      {/* Input - native scrolling for overflow text */}
      <input
        type="text"
        value={value ?? ''}
        onChange={(e) => onChange?.(e.target.value)}
        placeholder={placeholder}
        className={cn(
          // Fill remaining space
          'flex-1',
          'min-w-0',
          'bg-transparent',
          'border-none',
          'outline-none',
          // Text
          'text-sm',
          'text-text-primary',
          'placeholder:text-text-secondary',
          // Ensure clickable
          'cursor-text'
        )}
      />
    </label>
  )
}

export default SearchInput
