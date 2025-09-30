interface RegisterFormProps {
  className?: string
  children?: React.ReactNode
}

export default function RegisterForm({ className, children }: RegisterFormProps) {
  return (
    <div className={className}>
      <h2 className="text-2xl font-bold mb-4">RegisterForm</h2>
      {children}
    </div>
  )
}