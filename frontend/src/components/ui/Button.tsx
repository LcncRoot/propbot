import { cn } from '@/lib/utils'

interface ButtonProps {
  children: React.ReactNode
  /** Button variant */
  variant?: 'primary' | 'secondary' | 'ghost'
  /** Size variant */
  size?: 'sm' | 'md' | 'lg'
  /** Full width */
  fullWidth?: boolean
  /** Disabled state */
  disabled?: boolean
  /** Button type */
  type?: 'button' | 'submit' | 'reset'
  /** Optional icon (left) */
  icon?: React.ReactNode
  /** Click handler */
  onClick?: () => void
  className?: string
}

/**
 * Button - Primary (outlined cyan) and secondary (ghost) variants
 *
 * Variants:
 * - primary: Cyan outline with glow on hover
 * - secondary: Subtle background, no border
 * - ghost: Transparent, text only
 */
export function Button({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  disabled = false,
  type = 'button',
  icon,
  onClick,
  className,
}: ButtonProps) {
  const sizes = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-2.5 text-base',
  }

  const variants = {
    primary: cn(
      // Border & background
      'border border-accent-cyan',
      'bg-transparent',
      // Text
      'text-accent-cyan',
      // Hover
      'hover:bg-accent-cyan/10',
      'hover:shadow-glow-cyan',
      // Active
      'active:bg-accent-cyan/20'
    ),
    secondary: cn(
      // Border & background
      'border border-border-default',
      'bg-bg-card',
      // Text
      'text-text-primary',
      // Hover
      'hover:bg-bg-card-hover',
      'hover:border-border-default',
      // Active
      'active:bg-bg-selected'
    ),
    ghost: cn(
      // Border & background
      'border border-transparent',
      'bg-transparent',
      // Text
      'text-text-secondary',
      // Hover
      'hover:text-text-primary',
      'hover:bg-bg-card-hover',
      // Active
      'active:bg-bg-card'
    ),
  }

  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={cn(
        // Layout
        'inline-flex items-center justify-center gap-2',
        fullWidth && 'w-full',
        // Size
        sizes[size],
        // Shape
        'rounded-lg',
        // Font
        'font-medium',
        // Variant styles
        variants[variant],
        // Transitions
        'transition-all duration-200',
        // Disabled state
        disabled && 'opacity-50 cursor-not-allowed pointer-events-none',
        // Focus
        'focus-ring',
        // Custom classes
        className
      )}
    >
      {icon && (
        <span className="w-4 h-4 flex-shrink-0">
          {icon}
        </span>
      )}
      {children}
    </button>
  )
}

export default Button
