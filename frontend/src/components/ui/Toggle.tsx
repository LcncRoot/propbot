import { cn } from '@/lib/utils'

interface ToggleProps {
  /** Whether the toggle is on */
  checked?: boolean
  /** Change handler */
  onChange?: (checked: boolean) => void
  /** Disable the toggle */
  disabled?: boolean
  /** Size variant */
  size?: 'sm' | 'md'
  /** Accessible label */
  label?: string
  className?: string
}

/**
 * Toggle - Pill-shaped switch
 *
 * Features:
 * - Smooth sliding animation
 * - Teal color when on
 * - Accessible with keyboard support
 */
export function Toggle({
  checked = false,
  onChange,
  disabled = false,
  size = 'md',
  label,
  className,
}: ToggleProps) {
  const sizes = {
    sm: {
      track: 'w-9 h-5',
      thumb: 'w-4 h-4',
      translate: 'translate-x-4',
    },
    md: {
      track: 'w-11 h-6',
      thumb: 'w-5 h-5',
      translate: 'translate-x-5',
    },
  }

  const s = sizes[size]

  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={label}
      disabled={disabled}
      onClick={() => onChange?.(!checked)}
      className={cn(
        // Track layout
        'relative inline-flex items-center',
        'flex-shrink-0',
        s.track,
        'rounded-full',
        // Track background
        checked ? 'bg-accent-teal' : 'bg-border-default',
        // Border
        'border-2 border-transparent',
        // Transitions
        'transition-colors duration-200',
        // Cursor
        disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer',
        // Focus
        'focus-ring',
        // Custom classes
        className
      )}
    >
      {/* Thumb */}
      <span
        className={cn(
          // Size
          s.thumb,
          // Shape
          'rounded-full',
          // Background
          'bg-white',
          // Shadow
          'shadow-sm',
          // Position
          'transform transition-transform duration-200',
          checked ? s.translate : 'translate-x-0.5'
        )}
      />
    </button>
  )
}

export default Toggle
