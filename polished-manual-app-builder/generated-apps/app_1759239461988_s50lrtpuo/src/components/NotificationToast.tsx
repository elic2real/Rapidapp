interface NotificationToastProps {
  className?: string
  children?: React.ReactNode
}

export default function NotificationToast({ className, children }: NotificationToastProps) {
  return (
    <div className={className}>
      <h2 className="text-2xl font-bold mb-4">NotificationToast</h2>
      {children}
    </div>
  )
}