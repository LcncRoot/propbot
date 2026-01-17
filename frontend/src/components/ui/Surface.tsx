import { cn } from '@/lib/utils'

interface SurfaceProps {
  children: React.ReactNode
  className?: string
  /** Use gradient background instead of solid */
  gradient?: boolean
}

/**
 * Surface - Background container component
 *
 * Provides the base layer for content areas with optional gradient.
 * Use as a wrapper for main content sections.
 */
export function Surface({ children, className, gradient = false }: SurfaceProps) {
  return (
    <div
      className={cn(
        // Base styles
        'min-h-screen',
        // Background
        gradient ? 'surface-gradient' : 'bg-bg-surface',
        // Custom classes
        className
      )}
    >
      {children}
    </div>
  )
}

export default Surface
