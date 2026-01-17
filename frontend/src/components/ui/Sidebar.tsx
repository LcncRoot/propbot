import { cn } from '@/lib/utils'

interface SidebarProps {
  children: React.ReactNode
  className?: string
  /** Position: left or right side of screen */
  position?: 'left' | 'right'
}

/**
 * Sidebar - Vertical navigation container
 *
 * Fixed-position sidebar for icon navigation.
 * Contains SidebarItem components.
 */
export function Sidebar({
  children,
  className,
  position = 'left',
}: SidebarProps) {
  return (
    <aside
      className={cn(
        // Layout
        'fixed top-0 h-screen',
        'flex flex-col',
        'py-6 px-3',
        // Width
        'w-16',
        // Background
        'bg-bg-base',
        // Border
        position === 'left' ? 'border-r' : 'border-l',
        'border-border-default',
        // Z-index
        'z-50',
        // Position
        position === 'left' ? 'left-0' : 'right-0',
        // Custom classes
        className
      )}
    >
      {children}
    </aside>
  )
}

export default Sidebar
