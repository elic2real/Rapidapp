import { Button } from '@/components/Button'
import Link from 'next/link'

export default function HomePage() {
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Hero Section */}
      <section className="text-center py-16">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          Welcome to ADemoCrmApp
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          A demo CRM app with authentication, dashboard, and notifications. Stack: nextjs-postgres
        </p>
        <div className="space-x-4">
          <Button asChild>
            <Link href="/dashboard">Get Started</Link>
          </Button>
          <Button variant="outline" asChild>
            <Link href="/about">Learn More</Link>
          </Button>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16">
        <h2 className="text-3xl font-bold text-center mb-12">Features</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-3">User Authentication</h3>
            <p className="text-gray-600">
              Experience the power of user authentication in our modern application.
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-3">Real-time Updates</h3>
            <p className="text-gray-600">
              Experience the power of real-time updates in our modern application.
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-3">Admin Dashboard</h3>
            <p className="text-gray-600">
              Experience the power of admin dashboard in our modern application.
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-3">Email Notifications</h3>
            <p className="text-gray-600">
              Experience the power of email notifications in our modern application.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-primary-50 py-16 px-8 rounded-lg text-center">
        <h2 className="text-3xl font-bold mb-4">Ready to get started?</h2>
        <p className="text-lg text-gray-600 mb-8">
          Join thousands of users who are already using ADemoCrmApp.
        </p>
        <Button size="lg" asChild>
          <Link href="/register">Sign Up Now</Link>
        </Button>
      </section>
    </div>
  )
}