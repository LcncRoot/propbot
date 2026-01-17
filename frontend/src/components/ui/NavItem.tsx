import { cn } from '@/lib/utils'

interface NavItemProps {
  /** Icon element */
  icon: React.ReactNode
  /** Navigation label */
  label: string
  /** Whether this item is currently selected */
  selected?: boolean
  /** Optional badge/count */
  badge?: number | string
  /** Click handler */
  onClick?: () => void
  className?: string
}

/**
 * NavItem - Sidebar menu item with icon and label
 *
 * Horizontal layout with icon left, label right.
 * Selected state shows cyan accent.
 */
export function NavItem({
  icon,
  label,
  selected = false,
  badge,
  onClick,
  className,
}: NavItemProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        // Layout
        'flex items-center gap-3',
        'w-full',
        'px-3 py-2.5',
        'rounded-lg',
        // Base styles
        'text-left',
        'border border-transparent',
        // Text color
        selected ? 'text-text-primary' : 'text-text-secondary',
        // Background
        selected && 'bg-bg-selected',
        // Transitions
        'transition-all duration-200',
        // Hover state (when not selected)
        !selected && [
          'hover:bg-bg-card-hover',
          'hover:text-text-primary',
        ],
        // Cursor
        'cursor-pointer',
        // Focus
        'focus-ring',
        // Custom classes
        className
      )}
    >
      {/* Icon */}
      <span
        className={cn(
          'flex-shrink-0',
          'w-5 h-5',
          selected ? 'text-accent-cyan' : 'text-text-secondary',
          'transition-colors duration-200'
        )}
      >
        {icon}
      </span>

      {/* Label */}
      <span className="flex-1 text-sm font-medium truncate">
        {label}
      </span>

      {/* Badge */}
      {badge !== undefined && (
        <span
          className={cn(
            'flex-shrink-0',
            'px-2 py-0.5',
            'text-xs font-medium',
            'rounded-full',
            selected
              ? 'bg-accent-cyan/20 text-accent-cyan'
              : 'bg-bg-card text-text-secondary'
          )}
        >
          {badge}
        </span>
      )}

      {/* Selected indicator bar */}
      {selected && (
        <span
          className={cn(
            'absolute left-0 top-1/2 -translate-y-1/2',
            'w-0.5 h-5',
            'bg-accent-cyan',
            'rounded-r-full'
          )}
        />
      )}
    </button>
  )
}

export default NavItem
