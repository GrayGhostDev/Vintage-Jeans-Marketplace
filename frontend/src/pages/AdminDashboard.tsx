import { useAuth } from '../lib/auth'

export default function AdminDashboard() {
  const { user, logout } = useAuth()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <span className="text-xl font-bold text-indigo-600">Vintage Jeans - Admin</span>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-700">Admin: {user?.full_name}</span>
              <button
                onClick={logout}
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="mt-2 text-gray-600">Platform analytics, listing approvals, and seller management</p>
        </div>

        {/* Platform KPIs */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500">Total Sellers</div>
            <div className="mt-2 text-3xl font-bold text-gray-900">0</div>
            <div className="mt-1 text-sm text-green-600">+0 this week</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500">Total Listings</div>
            <div className="mt-2 text-3xl font-bold text-indigo-600">0</div>
            <div className="mt-1 text-sm text-gray-500">0 active</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500">Pending Approvals</div>
            <div className="mt-2 text-3xl font-bold text-yellow-600">0</div>
            <div className="mt-1 text-sm text-gray-500">Requires review</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500">Avg ROI</div>
            <div className="mt-2 text-3xl font-bold text-green-600">—%</div>
            <div className="mt-1 text-sm text-gray-500">Platform average</div>
          </div>
        </div>

        {/* Approval Queue */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Pending Approvals</h3>
          </div>
          <div className="px-6 py-12 text-center text-gray-500">
            <p className="text-lg font-medium mb-2">No pending approvals</p>
            <p className="text-sm">All listings have been reviewed</p>
          </div>
        </div>

        {/* Platform Analytics */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Listings by Platform</h3>
            <div className="space-y-3">
              {['Manual', 'eBay', 'Etsy', 'Whatnot'].map((platform) => (
                <div key={platform} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">{platform}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div className="bg-indigo-600 h-2 rounded-full" style={{ width: '0%' }}></div>
                    </div>
                    <span className="text-sm font-medium text-gray-900 w-8 text-right">0</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Brands</h3>
            <div className="space-y-3">
              {['Levi\'s', 'Wrangler', 'Lee', 'Vintage'].map((brand) => (
                <div key={brand} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">{brand}</span>
                  <span className="text-sm font-medium text-gray-900">0</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Market Insights */}
        <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg shadow-lg p-6 text-white">
          <h3 className="text-lg font-semibold mb-4">High-ROI Opportunities</h3>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
            <p className="text-sm opacity-90 mb-2">
              Based on recent market data, Japanese buyers are paying premium prices for:
            </p>
            <ul className="list-disc list-inside text-sm space-y-1 opacity-90">
              <li>1950s Levi's 501 with selvedge denim (3-5x US prices)</li>
              <li>1970s Wrangler with original tags (200-300% ROI)</li>
              <li>Rare Lee Riders from 1940s-1960s (up to 1000% ROI)</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
