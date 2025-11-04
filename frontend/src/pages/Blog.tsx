import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { blog } from '../lib/api'
import SEO from '../components/SEO'
import { BreadcrumbSchema } from '../components/SchemaMarkup'
import Navigation from '../components/Navigation'
import Footer from '../components/Footer'

export default function Blog() {
  const { data: posts, isLoading } = useQuery({
    queryKey: ['blog'],
    queryFn: async () => {
      const response = await blog.list()
      return response.data
    },
  })

  const featuredPosts = posts?.filter(p => p.featured).slice(0, 3)
  const recentPosts = posts?.slice(0, 12)

  return (
    <>
      <SEO
        title="Vintage Jeans Blog | Selling Tips, Market Insights & Collector Guides"
        description="Expert guides on selling vintage denim, pricing rare Levi's, finding high-ROI vintage jeans, and connecting with global collectors. Learn from market insights and seller success stories."
        keywords="vintage jeans blog, sell vintage denim tips, vintage Levi's pricing guide, vintage jeans market insights, how to sell vintage jeans"
        ogType="website"
      />
      <BreadcrumbSchema
        items={[
          { name: 'Home', url: '/' },
          { name: 'Blog', url: '/blog' },
        ]}
      />

      <div className="min-h-screen bg-white flex flex-col">
        <Navigation />

        {/* Hero Section */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h1 className="text-4xl font-bold mb-4">Vintage Jeans Blog</h1>
            <p className="text-xl opacity-90">
              Expert guides on selling vintage denim, market insights, and collector stories
            </p>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Featured Posts */}
          {featuredPosts && featuredPosts.length > 0 && (
            <div className="mb-16">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Featured Articles</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {featuredPosts.map((post) => (
                  <Link
                    key={post.id}
                    to={`/blog/${post.slug}`}
                    className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow"
                  >
                    <div className="h-48 bg-gradient-to-br from-indigo-500 to-purple-600"></div>
                    <div className="p-6">
                      <div className="text-sm text-indigo-600 font-medium mb-2">
                        {post.category.replace('_', ' ').toUpperCase()}
                      </div>
                      <h3 className="text-xl font-bold text-gray-900 mb-2">{post.title}</h3>
                      <p className="text-gray-600 mb-4">{post.excerpt}</p>
                      <div className="flex items-center text-sm text-gray-500">
                        <span>{post.read_time_minutes} min read</span>
                        <span className="mx-2">•</span>
                        <span>{post.view_count} views</span>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}

          {/* All Posts */}
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Recent Articles</h2>
            {isLoading ? (
              <p className="text-gray-500">Loading articles...</p>
            ) : recentPosts && recentPosts.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {recentPosts.map((post) => (
                  <Link
                    key={post.id}
                    to={`/blog/${post.slug}`}
                    className="bg-white rounded-lg shadow hover:shadow-md transition-shadow p-6"
                  >
                    <div className="text-xs text-indigo-600 font-medium mb-2">
                      {post.category.replace('_', ' ').toUpperCase()}
                    </div>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">{post.title}</h3>
                    <p className="text-gray-600 text-sm mb-4 line-clamp-3">{post.excerpt}</p>
                    <div className="flex items-center text-xs text-gray-500">
                      <span>{post.author}</span>
                      <span className="mx-2">•</span>
                      <span>{post.read_time_minutes} min</span>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">No articles published yet</p>
                <p className="text-gray-400 text-sm mt-2">Check back soon for expert guides and market insights</p>
              </div>
            )}
          </div>
        </div>

        <Footer />
      </div>
    </>
  )
}
