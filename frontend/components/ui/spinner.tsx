import { Loader2Icon, Sparkles, User as UserIcon, Eye, Shield } from 'lucide-react'

import { cn } from '@/lib/utils'

interface SpinnerProps extends React.ComponentProps<'svg'> {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  variant?: 'default' | 'dots' | 'pulse' | 'glow'
  text?: string
}

function Spinner({ className, size = 'md', variant = 'default', text, ...props }: SpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6', 
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  }

  const textSizes = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base', 
    xl: 'text-lg'
  }

  if (variant === 'dots') {
    return (
      <div className={cn("flex items-center gap-1", className)}>
        <div className="flex gap-1">
          <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
          <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>
        {text && <span className={cn("ml-2 text-muted-foreground", textSizes[size])}>{text}</span>}
      </div>
    )
  }

  if (variant === 'pulse') {
    return (
      <div className={cn("flex items-center justify-center", className)}>
        <div className="relative">
          <Sparkles className={cn("text-primary animate-pulse", sizeClasses[size])} />
          <div className="absolute inset-0 bg-primary/20 rounded-full animate-ping" />
        </div>
        {text && <span className={cn("ml-3 text-muted-foreground", textSizes[size])}>{text}</span>}
      </div>
    )
  }

  if (variant === 'glow') {
    return (
      <div className={cn("flex items-center justify-center", className)}>
        <div className="relative">
          <Loader2Icon
            role="status"
            aria-label="Loading"
            className={cn('text-primary animate-spin', sizeClasses[size])}
            {...props}
          />
          <div className="absolute inset-0 bg-primary/20 rounded-full animate-pulse blur-sm" />
        </div>
        {text && <span className={cn("ml-3 text-muted-foreground", textSizes[size])}>{text}</span>}
      </div>
    )
  }

  // Default variant
  return (
    <div className={cn("flex items-center", className)}>
      <Loader2Icon
        role="status"
        aria-label="Loading"
        className={cn('text-primary animate-spin', sizeClasses[size])}
        {...props}
      />
      {text && <span className={cn("ml-2 text-muted-foreground", textSizes[size])}>{text}</span>}
    </div>
  )
}

interface FullPageLoaderProps {
  text?: string
  subtext?: string
}

function FullPageLoader({ text = "Loading...", subtext }: FullPageLoaderProps) {
  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="text-center space-y-4">
        <div className="relative inline-block">
          <div className="w-16 h-16 border-4 border-primary/20 rounded-full"></div>
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin absolute top-0 left-0"></div>
          <div className="absolute inset-0 flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-primary animate-pulse" />
          </div>
        </div>
        <div className="space-y-2">
          <p className="text-lg font-medium text-foreground">{text}</p>
          {subtext && <p className="text-sm text-muted-foreground">{subtext}</p>}
        </div>
        
        {/* Animated dots */}
        <div className="flex justify-center gap-1">
          <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
          <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>
      </div>
    </div>
  )
}

interface CardLoaderProps {
  lines?: number
  className?: string
}

function CardLoader({ lines = 3, className = "" }: CardLoaderProps) {
  return (
    <div className={cn("p-6 space-y-4", className)}>
      <div className="animate-pulse space-y-3">
        <div className="h-4 bg-primary/20 rounded w-3/4"></div>
        {Array.from({ length: lines - 1 }).map((_, i) => (
          <div key={i} className="h-4 bg-primary/20 rounded" style={{ width: `${Math.random() * 40 + 60}%` }}></div>
        ))}
      </div>
    </div>
  )
}

interface ButtonLoaderProps {
  children: React.ReactNode
  loading?: boolean
  className?: string
  disabled?: boolean
  type?: 'button' | 'submit' | 'reset'
  onClick?: () => void
}

function ButtonLoader({ 
  children, 
  loading = false, 
  className = "", 
  disabled = false,
  type = 'button',
  onClick 
}: ButtonLoaderProps) {
  return (
    <button
      type={type}
      disabled={disabled || loading}
      onClick={onClick}
      className={cn(
        "relative inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
        "bg-primary text-primary-foreground hover:bg-primary/90",
        "h-10 px-4 py-2",
        className
      )}
    >
      <div className={cn("flex items-center justify-center transition-opacity duration-200", loading ? "opacity-0" : "opacity-100")}>
        {children}
      </div>
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center">
          <Spinner size="sm" />
        </div>
      )}
    </button>
  )
}

interface GuestModeLoaderProps {
  text?: string
  subtext?: string
}

function GuestModeLoader({ text = "Entering Guest Mode...", subtext = "Setting up your experience" }: GuestModeLoaderProps) {
  return (
    <div className="fixed inset-0 bg-background/95 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="text-center space-y-4">
        {/* Professional spinner */}
        <div className="relative inline-flex items-center justify-center">
          <div className="w-12 h-12 border-2 border-primary/20 rounded-full"></div>
          <div className="w-12 h-12 border-2 border-primary border-t-transparent rounded-full animate-spin absolute top-0 left-0"></div>
          <div className="absolute inset-0 flex items-center justify-center">
            <UserIcon className="w-5 h-5 text-primary" />
          </div>
        </div>
        
        <div className="space-y-1">
          <p className="text-lg font-medium text-foreground">{text}</p>
          {subtext && <p className="text-sm text-muted-foreground">{subtext}</p>}
        </div>
        
        {/* Simple progress dots */}
        <div className="flex justify-center gap-1">
          <div className="w-1.5 h-1.5 bg-primary rounded-full animate-pulse"></div>
          <div className="w-1.5 h-1.5 bg-primary rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
          <div className="w-1.5 h-1.5 bg-primary rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
        </div>
      </div>
    </div>
  )
}

export { Spinner, FullPageLoader, CardLoader, ButtonLoader, GuestModeLoader }
