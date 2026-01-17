import { cn } from '@/lib/utils'

interface SidebarItemProps {
  /** Icon element to display */
  icon: React.ReactNode
  /** Accessible label for the button */
  label: string
  /** Whether this item is currently selected */
  selected?: boolean
  /** Click handler */
  onClick?: () => void
  className?: string
}

/**
 * SidebarItem - Icon button for sidebar navigation
 *
 * Features:
 * - Centered icon display
 * - Selected state with cyan accent
 * - Hover state with background change
 * - Accessible button with aria-label
 */
export function SidebarItem({
  icon,
  label,
  selected = false,
  onClick,
  className,
}: SidebarItemProps) {
  return (
    <button
      onClick={onClick}
      aria-label={label}
      title={label}
      className={cn(
        // Layout
        'flex items-center justify-center',
        'w-10 h-10',
        'rounded-lg',
        // Base styles
        'border border-transparent',
        'text-text-secondary',
        // Transition
        'transition-all duration-200',
        // Hover state
        'hover:bg-bg-card-hover',
        'hover:text-text-primary',
        // Selected state
        selected && [
          'bg-bg-selected',
          'text-accent-cyan',
          'border-accent-cyan',
        ],
        // Focus state
        'focus-ring',
        // Custom classes
        className
      )}
    >
      {icon}
    </button>
  )
}

export default SidebarItem
