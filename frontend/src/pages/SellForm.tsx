import { useState } from 'react'
import { Link } from 'react-router-dom'
import Navigation from '../components/Navigation'
import Footer from '../components/Footer'
import SEO from '../components/SEO'

export default function SellForm() {
  const [formData, setFormData] = useState({
    brand: '',
    model: '',
    title: '',
    description: '',
    decade: '',
    waist_size: '',
    inseam: '',
    condition: 'excellent',
    price: '',
    purchase_price: '',
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev }
        delete newErrors[name]
        return newErrors
      })
    }
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.brand.trim()) newErrors.brand = 'Brand is required'
    if (!formData.title.trim()) newErrors.title = 'Title is required'
    if (!formData.description.trim()) newErrors.description = 'Description is required'
    if (!formData.price || parseFloat(formData.price) <= 0) {
      newErrors.price = 'Valid price is required'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)

    // Simulate API call
    setTimeout(() => {
      alert('Listing submitted successfully! (Demo mode - please create an account to save listings)')
      setIsSubmitting(false)
    }, 1500)
  }

  return (
    <>
      <SEO
        title="List Vintage Jeans | Sell Your Vintage Denim"
        description="List your vintage jeans for sale on our AI-powered marketplace. Get instant pricing suggestions and reach global vintage denim collectors."
        keywords="list vintage jeans, sell vintage denim, vintage jeans listing, sell Levi's online"
        ogType="website"
      />
      <div className="min-h-screen bg-white flex flex-col">
        <Navigation />

        <div className="flex-1 bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto">
            <div className="text-center mb-8">
              <h1 className="text-4xl font-extrabold text-gray-900 mb-3">List Your Vintage Jeans</h1>
              <p className="text-lg text-gray-600">
                Fill out the form below to list your vintage jeans. Our AI will analyze and suggest optimal pricing.
              </p>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-8">
              <div className="bg-indigo-50 border-l-4 border-indigo-600 p-4 mb-8 rounded-r-md">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-indigo-600" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-indigo-700">
                      <strong>Pro tip:</strong> To access full features, save listings, and manage your inventory, please{' '}
                      <Link to="/register" className="underline font-semibold hover:text-indigo-800">
                        create a seller account
                      </Link>
                      {' '}— it's free!
                    </p>
                  </div>
                </div>
              </div>

              <form className="space-y-6" onSubmit={handleSubmit}>
                {/* Brand and Model */}
                <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                  <div>
                    <label htmlFor="brand" className="block text-sm font-semibold text-gray-700 mb-2">
                      Brand <span className="text-red-500">*</span>
                    </label>
                    <input
                      id="brand"
                      name="brand"
                      type="text"
                      value={formData.brand}
                      onChange={handleChange}
                      placeholder="Levi's, Wrangler, Lee..."
                      className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                        errors.brand ? 'border-red-500' : 'border-gray-300'
                      }`}
                    />
                    {errors.brand && <p className="mt-1 text-sm text-red-500">{errors.brand}</p>}
                  </div>
                  <div>
                    <label htmlFor="model" className="block text-sm font-semibold text-gray-700 mb-2">
                      Model
                    </label>
                    <input
                      id="model"
                      name="model"
                      type="text"
                      value={formData.model}
                      onChange={handleChange}
                      placeholder="501, 505, 517..."
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                </div>

                {/* Title */}
                <div>
                  <label htmlFor="title" className="block text-sm font-semibold text-gray-700 mb-2">
                    Listing Title <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="title"
                    name="title"
                    type="text"
                    value={formData.title}
                    onChange={handleChange}
                    placeholder="Vintage Levi's 501 Jeans 1950s Selvedge Denim"
                    className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                      errors.title ? 'border-red-500' : 'border-gray-300'
                    }`}
                  />
                  {errors.title && <p className="mt-1 text-sm text-red-500">{errors.title}</p>}
                  <p className="mt-1 text-sm text-gray-500">Make it descriptive and keyword-rich for better visibility</p>
                </div>

                {/* Description */}
                <div>
                  <label htmlFor="description" className="block text-sm font-semibold text-gray-700 mb-2">
                    Description <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    id="description"
                    name="description"
                    rows={5}
                    value={formData.description}
                    onChange={handleChange}
                    placeholder="Describe the jeans: condition details, unique features, history, measurements, material composition..."
                    className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                      errors.description ? 'border-red-500' : 'border-gray-300'
                    }`}
                  />
                  {errors.description && <p className="mt-1 text-sm text-red-500">{errors.description}</p>}
                  <p className="mt-1 text-sm text-gray-500">Include measurements, flaws, and what makes these jeans special</p>
                </div>

                {/* Decade, Waist, Inseam */}
                <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
                  <div>
                    <label htmlFor="decade" className="block text-sm font-semibold text-gray-700 mb-2">
                      Decade/Era
                    </label>
                    <select
                      id="decade"
                      name="decade"
                      value={formData.decade}
                      onChange={handleChange}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                      <option value="">Select...</option>
                      <option value="1930s">1930s</option>
                      <option value="1940s">1940s</option>
                      <option value="1950s">1950s</option>
                      <option value="1960s">1960s</option>
                      <option value="1970s">1970s</option>
                      <option value="1980s">1980s</option>
                      <option value="1990s">1990s</option>
                      <option value="2000s">2000s</option>
                    </select>
                  </div>
                  <div>
                    <label htmlFor="waist_size" className="block text-sm font-semibold text-gray-700 mb-2">
                      Waist Size
                    </label>
                    <input
                      id="waist_size"
                      name="waist_size"
                      type="number"
                      value={formData.waist_size}
                      onChange={handleChange}
                      placeholder="32"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                  <div>
                    <label htmlFor="inseam" className="block text-sm font-semibold text-gray-700 mb-2">
                      Inseam
                    </label>
                    <input
                      id="inseam"
                      name="inseam"
                      type="number"
                      value={formData.inseam}
                      onChange={handleChange}
                      placeholder="34"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                </div>

                {/* Condition and Price */}
                <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                  <div>
                    <label htmlFor="condition" className="block text-sm font-semibold text-gray-700 mb-2">
                      Condition <span className="text-red-500">*</span>
                    </label>
                    <select
                      id="condition"
                      name="condition"
                      value={formData.condition}
                      onChange={handleChange}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                      <option value="new_with_tags">New with Tags</option>
                      <option value="excellent">Excellent (like new)</option>
                      <option value="very_good">Very Good (minor wear)</option>
                      <option value="good">Good (normal wear)</option>
                      <option value="fair">Fair (noticeable wear)</option>
                      <option value="poor">Poor (significant wear/damage)</option>
                    </select>
                  </div>
                  <div>
                    <label htmlFor="price" className="block text-sm font-semibold text-gray-700 mb-2">
                      Asking Price (USD) <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <span className="absolute left-4 top-2 text-gray-500">$</span>
                      <input
                        id="price"
                        name="price"
                        type="number"
                        step="0.01"
                        value={formData.price}
                        onChange={handleChange}
                        placeholder="150.00"
                        className={`w-full pl-8 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                          errors.price ? 'border-red-500' : 'border-gray-300'
                        }`}
                      />
                    </div>
                    {errors.price && <p className="mt-1 text-sm text-red-500">{errors.price}</p>}
                  </div>
                </div>

                {/* Purchase Price for ROI */}
                <div>
                  <label htmlFor="purchase_price" className="block text-sm font-semibold text-gray-700 mb-2">
                    Purchase Price (optional, for ROI tracking)
                  </label>
                  <div className="relative max-w-xs">
                    <span className="absolute left-4 top-2 text-gray-500">$</span>
                    <input
                      id="purchase_price"
                      name="purchase_price"
                      type="number"
                      step="0.01"
                      value={formData.purchase_price}
                      onChange={handleChange}
                      placeholder="50.00"
                      className="w-full pl-8 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                  <p className="mt-1 text-sm text-gray-500">Track your profit margins with our analytics dashboard</p>
                </div>

                {/* Submit Buttons */}
                <div className="flex flex-col sm:flex-row gap-4 pt-6 border-t">
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="flex-1 bg-indigo-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:-translate-y-0.5 shadow-lg"
                  >
                    {isSubmitting ? 'Submitting...' : 'Submit Listing'}
                  </button>
                  <Link
                    to="/"
                    className="flex-1 bg-gray-100 text-gray-700 py-3 px-6 rounded-lg font-semibold hover:bg-gray-200 text-center transition-all"
                  >
                    Cancel
                  </Link>
                </div>

                <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mt-6 rounded-r-md">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm text-yellow-700">
                        <strong>Demo mode:</strong> This form is for demonstration purposes. To save and manage real listings, please{' '}
                        <Link to="/register" className="underline font-semibold hover:text-yellow-800">
                          create a free account
                        </Link>.
                      </p>
                    </div>
                  </div>
                </div>
              </form>
            </div>

            {/* Benefits Section */}
            <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white rounded-lg shadow p-6 text-center">
                <div className="text-4xl mb-3">📊</div>
                <h3 className="font-bold text-gray-900 mb-2">AI-Powered Pricing</h3>
                <p className="text-sm text-gray-600">Get instant pricing suggestions based on market data</p>
              </div>
              <div className="bg-white rounded-lg shadow p-6 text-center">
                <div className="text-4xl mb-3">🌍</div>
                <h3 className="font-bold text-gray-900 mb-2">Global Reach</h3>
                <p className="text-sm text-gray-600">Your listings reach collectors in 45+ countries</p>
              </div>
              <div className="bg-white rounded-lg shadow p-6 text-center">
                <div className="text-4xl mb-3">💰</div>
                <h3 className="font-bold text-gray-900 mb-2">ROI Tracking</h3>
                <p className="text-sm text-gray-600">Monitor profits with detailed analytics dashboard</p>
              </div>
            </div>
          </div>
        </div>

        <Footer />
      </div>
    </>
  )
}
