interface LoginFormProps {
  className?: string
  children?: React.ReactNode
}

export default function LoginForm({ className, children }: LoginFormProps) {
  return (
    <div className={className}>
      <h2 className="text-2xl font-bold mb-4">LoginForm</h2>
      {children}
    </div>
  )
}