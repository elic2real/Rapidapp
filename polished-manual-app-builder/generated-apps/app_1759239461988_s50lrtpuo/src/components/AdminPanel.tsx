interface AdminPanelProps {
  className?: string
  children?: React.ReactNode
}

export default function AdminPanel({ className, children }: AdminPanelProps) {
  return (
    <div className={className}>
      <h2 className="text-2xl font-bold mb-4">AdminPanel</h2>
      {children}
    </div>
  )
}