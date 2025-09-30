import Link from 'next/link'

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-12">
        <div className="grid md:grid-cols-4 gap-8">
          <div className="col-span-2">
            <h3 className="text-lg font-semibold mb-4">ADemoCrmApp</h3>
            <p className="text-gray-400 mb-4">
              A demo CRM app with authentication, dashboard, and notifications. Stack: nextjs-postgres
            </p>
            <div className="flex space-x-4">
              <a href="#" className="text-gray-400 hover:text-white">
                <span className="sr-only">Twitter</span>
                🐦
              </a>
              <a href="#" className="text-gray-400 hover:text-white">
                <span className="sr-only">GitHub</span>
                🐙
              </a>
              <a href="#" className="text-gray-400 hover:text-white">
                <span className="sr-only">LinkedIn</span>
                💼
              </a>
            </div>
          </div>
          
          <div>
            <h4 className="text-sm font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2">
              
              <li>
                <Link href="/home" className="text-gray-400 hover:text-white">
                  Home
                </Link>
              </li>
              <li>
                <Link href="/login" className="text-gray-400 hover:text-white">
                  Login
                </Link>
              </li>
              <li>
                <Link href="/register" className="text-gray-400 hover:text-white">
                  Register
                </Link>
              </li>
              <li>
                <Link href="/profile" className="text-gray-400 hover:text-white">
                  Profile
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-sm font-semibold mb-4">Support</h4>
            <ul className="space-y-2">
              <li>
                <Link href="/help" className="text-gray-400 hover:text-white">
                  Help Center
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-gray-400 hover:text-white">
                  Contact Us
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="text-gray-400 hover:text-white">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="/terms" className="text-gray-400 hover:text-white">
                  Terms of Service
                </Link>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
          <p>&copy; {new Date().getFullYear()} ADemoCrmApp. All rights reserved.</p>
          <p className="mt-2 text-sm">Built with ❤️ using Rapidapp AI Generator</p>
        </div>
      </div>
    </footer>
  )
}