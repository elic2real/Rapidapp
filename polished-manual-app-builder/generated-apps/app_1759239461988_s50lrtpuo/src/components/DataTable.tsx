interface DataTableProps {
  className?: string
  children?: React.ReactNode
}

export default function DataTable({ className, children }: DataTableProps) {
  return (
    <div className={className}>
      <h2 className="text-2xl font-bold mb-4">DataTable</h2>
      {children}
    </div>
  )
}