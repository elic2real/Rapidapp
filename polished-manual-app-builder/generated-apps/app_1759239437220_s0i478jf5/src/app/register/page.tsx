export default function RegisterPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Register</h1>
        
        <div className="bg-white rounded-lg shadow-md p-8">
          <p className="text-lg text-gray-600 mb-6">
            Welcome to the register page of ADemoCrmApp.
          </p>
          
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h2 className="text-2xl font-semibold mb-4">Features</h2>
              <ul className="space-y-2">
                
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-primary-500 rounded-full mr-3"></span>
                  User Authentication
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-primary-500 rounded-full mr-3"></span>
                  Real-time Updates
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-primary-500 rounded-full mr-3"></span>
                  Admin Dashboard
                </li>
                <li className="flex items-center">
                  <span className="w-2 h-2 bg-primary-500 rounded-full mr-3"></span>
                  Email Notifications
                </li>
              </ul>
            </div>
            
            <div>
              <h2 className="text-2xl font-semibold mb-4">Information</h2>
              <p className="text-gray-600">
                This register page is part of your ADemoCrmApp application.
                It's built with modern technologies and best practices.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}