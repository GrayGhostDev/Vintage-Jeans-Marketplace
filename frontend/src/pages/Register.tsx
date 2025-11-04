import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { auth } from '../lib/api'
import Navigation from '../components/Navigation'
import Footer from '../components/Footer'
import SEO from '../components/SEO'

export default function Register() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    business_name: '',
    location: '',
    referred_by_code: '',
  })
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const registerMutation = useMutation({
    mutationFn: (data: typeof formData) => auth.register(data),
    onSuccess: () => {
      navigate('/login', {
        state: { message: 'Registration successful! Please log in.' },
      })
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    registerMutation.mutate(formData)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }))
  }

  return (
    <>
      <SEO
        title="Create Seller Account | Vintage Jeans Marketplace"
        description="Join the Vintage Jeans Marketplace. Create your free seller account and start listing vintage denim to buyers worldwide. AI-powered analytics included."
        keywords="create seller account, register vintage jeans, sell vintage denim, vintage jeans seller signup"
        ogType="website"
      />
      <div className="min-h-screen bg-white flex flex-col">
        <Navigation />

        <div className="flex-1 bg-gradient-to-br from-indigo-50 via-white to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-md mx-auto">
            <div>
              <h2 className="text-center text-3xl font-extrabold text-gray-900">
                Create your seller account
              </h2>
              <p className="mt-2 text-center text-sm text-gray-600">
                Already have an account?{' '}
                <Link to="/login" className="font-medium text-indigo-600 hover:text-indigo-500">
                  Sign in
                </Link>
              </p>
            </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md text-sm">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Email address *
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={formData.email}
                onChange={handleChange}
                className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Password *
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={formData.password}
                onChange={handleChange}
                className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-1">
                Full Name *
              </label>
              <input
                id="full_name"
                name="full_name"
                type="text"
                required
                value={formData.full_name}
                onChange={handleChange}
                className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label htmlFor="business_name" className="block text-sm font-medium text-gray-700 mb-1">
                Business Name (optional)
              </label>
              <input
                id="business_name"
                name="business_name"
                type="text"
                value={formData.business_name}
                onChange={handleChange}
                className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-1">
                Location (City, Country) *
              </label>
              <input
                id="location"
                name="location"
                type="text"
                required
                placeholder="Los Angeles, USA"
                value={formData.location}
                onChange={handleChange}
                className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label htmlFor="referred_by_code" className="block text-sm font-medium text-gray-700 mb-1">
                Referral Code (optional)
              </label>
              <input
                id="referred_by_code"
                name="referred_by_code"
                type="text"
                placeholder="VJ12345678"
                value={formData.referred_by_code}
                onChange={handleChange}
                className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={registerMutation.isPending}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {registerMutation.isPending ? 'Creating account...' : 'Create account'}
            </button>
          </div>

          <div className="text-center">
            <Link to="/" className="text-sm text-indigo-600 hover:text-indigo-500">
              ← Back to home
            </Link>
          </div>
        </form>
      </div>
    </div>

        <Footer />
      </div>
    </>
  )
}
