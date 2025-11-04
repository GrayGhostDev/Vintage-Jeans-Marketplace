import { Link } from 'react-router-dom'
import SEO from '../components/SEO'
import { OrganizationSchema } from '../components/SchemaMarkup'
import Navigation from '../components/Navigation'
import Footer from '../components/Footer'

export default function Landing() {
  return (
    <>
      <SEO
        title="Sell Vintage Jeans | List Your Vintage Levi's & Retro Denim"
        description="AI-powered marketplace for vintage denim. Sell vintage jeans from Levi's, Wrangler, Lee. Connect with global collectors. Free analytics. 4,900% ROI potential on rare vintage finds."
        keywords="sell vintage jeans, sell vintage denim, sell Levi's 501, vintage jeans marketplace, sell selvedge denim, sell 80s jeans, sell 90s vintage jeans, eco-friendly denim resale, vintage jeans Japan"
        ogType="website"
      />
      <OrganizationSchema
        name="Vintage Jeans Marketplace"
        url="https://vintagejeans.com"
        logo="https://vintagejeans.com/logo.png"
        description="AI-powered marketplace connecting vintage denim sellers with global collectors"
        sameAs={[
          'https://www.facebook.com/vintagejeans',
          'https://www.instagram.com/vintagejeans',
          'https://www.twitter.com/vintagejeans',
        ]}
      />

      <div className="min-h-screen bg-white">
        <Navigation />

        {/* Hero Section */}
        <section className="relative bg-gradient-to-br from-indigo-50 via-white to-purple-50 overflow-hidden">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-32">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              {/* Text Content */}
              <div className="text-center lg:text-left">
                <h1 className="text-5xl md:text-6xl lg:text-7xl font-extrabold text-gray-900 mb-6 leading-tight">
                  Turn Vintage Finds into
                  <span className="block text-indigo-600">Global Profits</span>
                </h1>
                <p className="text-xl md:text-2xl text-gray-600 mb-8 leading-relaxed">
                  AI-powered marketplace for vintage denim. List your finds, get instant analytics,
                  and discover high-ROI opportunities in the global vintage jeans market.
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                  <Link
                    to="/register"
                    className="px-8 py-4 text-lg font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-0.5"
                  >
                    Start Selling Free →
                  </Link>
                  <Link
                    to="/blog"
                    className="px-8 py-4 text-lg font-semibold text-indigo-600 bg-white border-2 border-indigo-600 rounded-lg hover:bg-indigo-50 transition-all"
                  >
                    Learn More
                  </Link>
                </div>

                {/* Trust Indicators */}
                <div className="mt-12 flex flex-wrap gap-6 justify-center lg:justify-start text-sm text-gray-600">
                  <div className="flex items-center gap-2">
                    <svg className="h-5 w-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span>Free to join</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <svg className="h-5 w-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span>AI-powered insights</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <svg className="h-5 w-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span>Global reach</span>
                  </div>
                </div>
              </div>

              {/* Visual Element */}
              <div className="relative lg:block">
                <div className="relative bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl p-8 shadow-2xl transform rotate-3 hover:rotate-0 transition-transform duration-300">
                  <div className="bg-white rounded-lg p-6 transform -rotate-3">
                    <div className="text-center">
                      <div className="text-6xl mb-4">👖</div>
                      <h3 className="text-2xl font-bold text-gray-900 mb-2">Real ROI Example</h3>
                      <div className="bg-gray-50 rounded-lg p-4 mb-4">
                        <p className="text-sm text-gray-600 mb-2">1950s Levi's 501</p>
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-xs text-gray-500">Bought</p>
                            <p className="text-lg font-bold text-gray-900">$50</p>
                          </div>
                          <div className="text-indigo-600">→</div>
                          <div>
                            <p className="text-xs text-gray-500">Sold</p>
                            <p className="text-lg font-bold text-green-600">$2,500</p>
                          </div>
                        </div>
                      </div>
                      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg p-4 text-white">
                        <p className="text-sm font-medium mb-1">Return on Investment</p>
                        <p className="text-4xl font-extrabold">4,900%</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Stats Section */}
        <section className="py-16 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              <div className="text-center">
                <div className="text-4xl font-extrabold text-indigo-600 mb-2">1000+</div>
                <div className="text-sm text-gray-600">Sellers Worldwide</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-extrabold text-indigo-600 mb-2">50K+</div>
                <div className="text-sm text-gray-600">Vintage Jeans Listed</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-extrabold text-indigo-600 mb-2">245%</div>
                <div className="text-sm text-gray-600">Avg ROI</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-extrabold text-indigo-600 mb-2">45+</div>
                <div className="text-sm text-gray-600">Countries Reached</div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-extrabold text-gray-900 mb-4">Why Sellers Choose Us</h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Everything you need to maximize profits on vintage denim sales
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {/* Feature 1 */}
              <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-shadow border border-gray-100">
                <div className="w-14 h-14 bg-indigo-100 rounded-lg flex items-center justify-center mb-6">
                  <svg className="w-8 h-8 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">Free Analytics</h3>
                <p className="text-gray-600 leading-relaxed">
                  AI-powered insights on pricing, trends, and market opportunities. Know exactly what to buy and where to sell for maximum ROI.
                </p>
              </div>

              {/* Feature 2 */}
              <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-shadow border border-gray-100">
                <div className="w-14 h-14 bg-purple-100 rounded-lg flex items-center justify-center mb-6">
                  <svg className="w-8 h-8 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">Global Reach</h3>
                <p className="text-gray-600 leading-relaxed">
                  Connect with buyers worldwide. Special focus on high-value markets like Japan where vintage Levi's can sell for thousands.
                </p>
              </div>

              {/* Feature 3 */}
              <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-shadow border border-gray-100">
                <div className="w-14 h-14 bg-green-100 rounded-lg flex items-center justify-center mb-6">
                  <svg className="w-8 h-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">Multi-Platform Sync</h3>
                <p className="text-gray-600 leading-relaxed">
                  Sync your listings from eBay, Etsy, Whatnot and more. Manage everything from one powerful dashboard with automated updates.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section className="py-20 bg-gradient-to-br from-gray-50 to-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-extrabold text-gray-900 mb-4">How It Works</h2>
              <p className="text-xl text-gray-600">Start selling in minutes</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
              <div className="relative">
                <div className="flex items-center justify-center w-16 h-16 bg-indigo-600 text-white rounded-full text-2xl font-bold mb-6 mx-auto">
                  1
                </div>
                <h3 className="text-xl font-bold text-gray-900 text-center mb-3">Create Account</h3>
                <p className="text-gray-600 text-center">
                  Sign up for free in under 2 minutes. No credit card required, no hidden fees.
                </p>
              </div>

              <div className="relative">
                <div className="flex items-center justify-center w-16 h-16 bg-indigo-600 text-white rounded-full text-2xl font-bold mb-6 mx-auto">
                  2
                </div>
                <h3 className="text-xl font-bold text-gray-900 text-center mb-3">List Your Jeans</h3>
                <p className="text-gray-600 text-center">
                  Upload photos, add details, and get AI-powered pricing suggestions instantly.
                </p>
              </div>

              <div className="relative">
                <div className="flex items-center justify-center w-16 h-16 bg-indigo-600 text-white rounded-full text-2xl font-bold mb-6 mx-auto">
                  3
                </div>
                <h3 className="text-xl font-bold text-gray-900 text-center mb-3">Connect & Sell</h3>
                <p className="text-gray-600 text-center">
                  Reach global collectors and track your sales performance with detailed analytics.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Social Proof / Testimonials */}
        <section className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-extrabold text-gray-900 mb-4">Seller Success Stories</h2>
              <p className="text-xl text-gray-600">Real results from real sellers</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-100">
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-bold text-lg">
                    MK
                  </div>
                  <div className="ml-4">
                    <div className="font-semibold text-gray-900">Michael K.</div>
                    <div className="text-sm text-gray-500">Los Angeles, CA</div>
                  </div>
                </div>
                <p className="text-gray-600 italic mb-4">
                  "Sold a pair of 1960s Levi's Big E for $800 to a collector in Tokyo. The AI pricing tool helped me realize what I had was worth 10x what I thought!"
                </p>
                <div className="text-sm text-indigo-600 font-medium">ROI: 1,500%</div>
              </div>

              <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-100">
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center text-purple-600 font-bold text-lg">
                    SL
                  </div>
                  <div className="ml-4">
                    <div className="font-semibold text-gray-900">Sarah L.</div>
                    <div className="text-sm text-gray-500">Portland, OR</div>
                  </div>
                </div>
                <p className="text-gray-600 italic mb-4">
                  "As a thrift store picker, this platform changed my business. The market insights show me exactly what to look for. Made $5K in my first month!"
                </p>
                <div className="text-sm text-purple-600 font-medium">Monthly Revenue: $5,000+</div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 bg-gradient-to-r from-indigo-600 to-purple-600">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-4xl md:text-5xl font-extrabold text-white mb-6">
              Ready to Start Selling?
            </h2>
            <p className="text-xl text-indigo-100 mb-10">
              Join thousands of sellers turning vintage finds into global profits
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/register"
                className="px-10 py-4 text-lg font-semibold text-indigo-600 bg-white rounded-lg hover:bg-gray-50 shadow-xl hover:shadow-2xl transition-all transform hover:-translate-y-0.5"
              >
                Get Started Free →
              </Link>
              <Link
                to="/blog"
                className="px-10 py-4 text-lg font-semibold text-white bg-indigo-700 bg-opacity-50 backdrop-blur-sm rounded-lg hover:bg-opacity-60 transition-all border-2 border-white border-opacity-30"
              >
                Learn More
              </Link>
            </div>
            <p className="mt-6 text-sm text-indigo-200">
              No credit card required • Free analytics • Cancel anytime
            </p>
          </div>
        </section>

        <Footer />
      </div>
    </>
  )
}
