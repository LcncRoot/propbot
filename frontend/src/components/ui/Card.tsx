import { cn } from '@/lib/utils'

interface CardProps {
  children: React.ReactNode
  className?: string
  /** Adds cyan border glow for active/selected state */
  active?: boolean
  /** Enables hover state with background change */
  hoverable?: boolean
  /** Click handler */
  onClick?: () => void
}

/**
 * Card - Rounded panel component
 *
 * Features:
 * - Subtle inner highlight on top edge
 * - Optional cyan glow border for active state
 * - Optional hover state with background change
 */
export function Card({
  children,
  className,
  active = false,
  hoverable = false,
  onClick,
}: CardProps) {
  return (
    <div
      onClick={onClick}
      className={cn(
        // Base styles
        'rounded-lg',
        'bg-bg-card',
        'border border-border-default',
        // Inner highlight (top edge subtle glow)
        'card-highlight',
        // Transition for smooth state changes
        'transition-all duration-200',
        // Hoverable state
        hoverable && [
          'cursor-pointer',
          'hover:bg-bg-card-hover',
          'hover:border-border-default',
        ],
        // Active state - cyan glow
        active && 'glow-cyan',
        // Custom classes
        className
      )}
    >
      {children}
    </div>
  )
}

export default Card
