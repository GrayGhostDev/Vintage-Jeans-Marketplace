import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { blog } from '../lib/api'
import { formatDate } from '../lib/utils'
import SEO from '../components/SEO'
import { ArticleSchema, BreadcrumbSchema } from '../components/SchemaMarkup'
import Navigation from '../components/Navigation'
import Footer from '../components/Footer'

export default function BlogArticle() {
  const { slug } = useParams<{ slug: string }>()

  const { data: post, isLoading } = useQuery({
    queryKey: ['blog', slug],
    queryFn: async () => {
      const response = await blog.get(slug!)
      return response.data
    },
    enabled: !!slug,
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-500">Loading article...</p>
      </div>
    )
  }

  if (!post) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Article not found</h1>
          <Link to="/blog" className="text-indigo-600 hover:text-indigo-700">
            ← Back to blog
          </Link>
        </div>
      </div>
    )
  }

  return (
    <>
      <SEO
        title={post.meta_title || post.title}
        description={post.meta_description || post.excerpt}
        keywords={post.meta_keywords || ''}
        ogType="article"
      />
      <ArticleSchema
        headline={post.title}
        description={post.excerpt}
        image={[post.featured_image_url || 'https://vintagejeans.com/og-default.jpg']}
        datePublished={post.published_at || post.created_at}
        dateModified={post.updated_at}
        author={post.author}
        publisher={{
          name: 'Vintage Jeans Marketplace',
          logo: 'https://vintagejeans.com/logo.png',
        }}
      />
      <BreadcrumbSchema
        items={[
          { name: 'Home', url: '/' },
          { name: 'Blog', url: '/blog' },
          { name: post.title, url: `/blog/${post.slug}` },
        ]}
      />

      <div className="min-h-screen bg-white flex flex-col">
        <Navigation />

        {/* Article */}
        <article className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="bg-white rounded-lg shadow-lg p-8 md:p-12">
            {/* Header */}
            <header className="mb-8">
              <div className="text-sm text-indigo-600 font-medium mb-4">
                {post.category.replace('_', ' ').toUpperCase()}
              </div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">{post.title}</h1>
              <div className="flex items-center text-sm text-gray-500">
                <span>{post.author}</span>
                <span className="mx-2">•</span>
                <span>{post.published_at ? formatDate(post.published_at) : formatDate(post.created_at)}</span>
                <span className="mx-2">•</span>
                <span>{post.read_time_minutes} min read</span>
                <span className="mx-2">•</span>
                <span>{post.view_count} views</span>
              </div>
            </header>

            {/* Featured Image */}
            {post.featured_image_url && (
              <div className="mb-8">
                <img
                  src={post.featured_image_url}
                  alt={post.featured_image_alt || post.title}
                  className="w-full h-96 object-cover rounded-lg"
                />
              </div>
            )}

            {/* Content */}
            <div className="prose prose-lg max-w-none">
              <div
                dangerouslySetInnerHTML={{ __html: post.content }}
                className="text-gray-700 leading-relaxed"
              />
            </div>

            {/* Tags */}
            {post.tags && (
              <div className="mt-12 pt-8 border-t">
                <div className="flex flex-wrap gap-2">
                  {JSON.parse(post.tags).map((tag: string, index: number) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-indigo-50 text-indigo-600 text-sm rounded-full"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* CTA */}
          <div className="mt-12 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg p-8 text-white text-center">
            <h3 className="text-2xl font-bold mb-4">Ready to Sell Your Vintage Jeans?</h3>
            <p className="text-lg opacity-90 mb-6">
              Join our marketplace and connect with global collectors
            </p>
            <Link
              to="/register"
              className="inline-block px-8 py-3 bg-white text-indigo-600 font-medium rounded-md hover:bg-gray-100 transition-colors"
            >
              Get Started Free
            </Link>
          </div>
        </article>

        <Footer />
      </div>
    </>
  )
}
