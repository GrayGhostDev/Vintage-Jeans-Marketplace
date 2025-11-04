import { useAuth } from '../lib/auth'
import { useQuery } from '@tanstack/react-query'
import { listings } from '../lib/api'
import { formatCurrency, calculateROI } from '../lib/utils'

export default function SellerDashboard() {
  const { user, logout } = useAuth()

  const { data: listingsData, isLoading } = useQuery({
    queryKey: ['listings'],
    queryFn: async () => {
      const response = await listings.list()
      return response.data
    },
  })

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <span className="text-xl font-bold text-indigo-600">Vintage Jeans</span>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-700">Welcome, {user?.full_name}</span>
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
          <h1 className="text-3xl font-bold text-gray-900">Seller Dashboard</h1>
          <p className="mt-2 text-gray-600">Manage your vintage jeans listings and track performance</p>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-3 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500">Total Listings</div>
            <div className="mt-2 text-3xl font-bold text-gray-900">{user?.total_listings || 0}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500">Active Listings</div>
            <div className="mt-2 text-3xl font-bold text-indigo-600">{user?.active_listings || 0}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500">Referral Code</div>
            <div className="mt-2 text-2xl font-mono text-gray-900">{user?.referral_code || 'N/A'}</div>
          </div>
        </div>

        {/* AI Recommendations Panel */}
        <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg shadow-lg p-6 mb-8 text-white">
          <h3 className="text-lg font-semibold mb-2">AI Recommendations</h3>
          <div className="space-y-2 text-sm">
            <p>• High demand detected for 1970s Levi's 501 in Japan market (+35% this month)</p>
            <p>• Consider pricing your 1950s selvedge denim at $300-$500 based on similar sales</p>
            <p>• Best time to list: Wednesday-Thursday, 10AM-2PM EST</p>
          </div>
        </div>

        {/* Listings Table */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-900">Your Listings</h3>
            <button className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 text-sm font-medium">
              + Add New Listing
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Item
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Brand / Decade
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Price
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ROI
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Views
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {isLoading ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                      Loading...
                    </td>
                  </tr>
                ) : listingsData && listingsData.length > 0 ? (
                  listingsData.map((listing) => (
                    <tr key={listing.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{listing.title}</div>
                        <div className="text-sm text-gray-500">{listing.platform}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{listing.brand}</div>
                        <div className="text-sm text-gray-500">{listing.decade || 'N/A'}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatCurrency(listing.price, listing.currency)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          listing.status === 'active' ? 'bg-green-100 text-green-800' :
                          listing.status === 'pending_approval' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {listing.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {listing.purchase_price ? (
                          <span className="text-green-600 font-medium">
                            +{calculateROI(listing.purchase_price, listing.price).toFixed(0)}%
                          </span>
                        ) : (
                          <span className="text-gray-400">—</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {listing.views}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center">
                      <div className="text-gray-500">
                        <p className="text-lg font-medium mb-2">No listings yet</p>
                        <p className="text-sm">Create your first listing to get started</p>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
