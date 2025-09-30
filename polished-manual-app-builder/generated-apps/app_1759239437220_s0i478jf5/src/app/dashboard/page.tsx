import { Card } from '@/components/Card'
import { Button } from '@/components/Button'

export default function DashboardPage() {
  const stats = [
    { label: 'Total Users', value: '1,234', change: '+12%' },
    { label: 'Active Sessions', value: '89', change: '+5%' },
    { label: 'Revenue', value: '$12,345', change: '+23%' },
    { label: 'Conversion Rate', value: '3.2%', change: '+8%' },
  ]

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Dashboard</h1>
        <p className="text-gray-600">Welcome back! Here's what's happening with your ADemoCrmApp.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, index) => (
          <Card key={index} className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">{stat.label}</p>
                <p className="text-2xl font-bold">{stat.value}</p>
                <p className="text-sm text-green-600">{stat.change}</p>
              </div>
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                📊
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-2 gap-8">
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="space-y-3">
            
            <Button variant="outline" className="w-full justify-start">
              ⚡ User Authentication
            </Button>
            <Button variant="outline" className="w-full justify-start">
              ⚡ Real-time Updates
            </Button>
            <Button variant="outline" className="w-full justify-start">
              ⚡ Admin Dashboard
            </Button>
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                👤
              </div>
              <div>
                <p className="font-medium">New user registered</p>
                <p className="text-sm text-gray-600">2 minutes ago</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                💰
              </div>
              <div>
                <p className="font-medium">Payment received</p>
                <p className="text-sm text-gray-600">1 hour ago</p>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}