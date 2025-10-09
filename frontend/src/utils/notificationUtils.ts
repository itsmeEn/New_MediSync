import { useQuasar } from 'quasar'

export interface NotificationOptions {
  message: string
  type?: 'positive' | 'negative' | 'warning' | 'info' | 'ongoing'
  timeout?: number
  position?: 'top' | 'top-left' | 'top-right' | 'bottom' | 'bottom-left' | 'bottom-right' | 'left' | 'right' | 'center'
  actions?: Array<{
    label?: string
    icon?: string
    color?: string
    handler?: () => void
  }>
  html?: boolean
  caption?: string
  avatar?: string
  icon?: string
  color?: string
  textColor?: string
  multiLine?: boolean
  classes?: string
  attrs?: Record<string, string | number | boolean>
  group?: boolean | string | number
  badgeColor?: string
  badgeTextColor?: string
  badgePosition?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right'
  progress?: boolean
  progressClass?: string
  spinner?: boolean
  spinnerColor?: string
  spinnerSize?: string
}

export function useNotifications() {
  const $q = useQuasar()

  const showNotification = (options: NotificationOptions) => {
    // Destructure options to exclude position, then force it to 'top'
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { position, ...restOptions } = options
    
    const notificationConfig = {
      timeout: 4000,
      textColor: 'white',
      actions: [{ icon: 'close', color: 'white' }],
      ...restOptions,
      // Force position to be top regardless of what's passed
      position: 'top' as const
    }

    return $q.notify(notificationConfig)
  }

  const showSuccess = (message: string, options?: Partial<NotificationOptions>) => {
    return showNotification({
      message,
      type: 'positive',
      icon: 'check_circle',
      color: 'positive',
      ...options
    })
  }

  const showError = (message: string, options?: Partial<NotificationOptions>) => {
    return showNotification({
      message,
      type: 'negative',
      icon: 'error',
      color: 'negative',
      ...options
    })
  }

  const showWarning = (message: string, options?: Partial<NotificationOptions>) => {
    return showNotification({
      message,
      type: 'warning',
      icon: 'warning',
      color: 'warning',
      ...options
    })
  }

  const showInfo = (message: string, options?: Partial<NotificationOptions>) => {
    return showNotification({
      message,
      type: 'info',
      icon: 'info',
      color: 'info',
      ...options
    })
  }

  return {
    showNotification,
    showSuccess,
    showError,
    showWarning,
    showInfo
  }
}