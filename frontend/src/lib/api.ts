import axios from 'axios'

// API Base URL from environment variable
// Development: http://localhost:8000/api
// Production: https://your-app.onrender.com/api
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

console.log('API Base URL:', API_BASE_URL)

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api

// Types
export interface Seller {
  id: string  // UUID
  email: string
  full_name: string
  business_name?: string
  location: string
  is_verified: boolean
  role: string
  total_listings: number
  active_listings: number
  referral_code?: string
  created_at: string
}

export interface Listing {
  id: string  // UUID
  seller_id: string  // UUID
  platform: string
  title: string
  description: string
  brand: string
  decade?: string
  model?: string
  waist_size?: number
  inseam_length?: number
  condition: string
  price: number
  currency: string
  purchase_price?: number
  status: string
  views: number
  favorites: number
  is_featured: boolean
  primary_image_url?: string
  created_at: string
  updated_at: string
}

// API functions

export const auth = {
  register: (data: any) => api.post('/sellers/register', data),
  login: (username: string, password: string) =>
    api.post('/sellers/login', new URLSearchParams({ username, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),
  getMe: () => api.get<Seller>('/sellers/me'),
  updateProfile: (data: any) => api.patch('/sellers/me', data),
}

export const listings = {
  list: (params?: any) => api.get<Listing[]>('/listings', { params }),
  get: (id: string) => api.get<Listing>(`/listings/${id}`),
  create: (data: any) => api.post<Listing>('/listings', data),
  update: (id: string, data: any) => api.patch<Listing>(`/listings/${id}`, data),
  delete: (id: string) => api.delete(`/listings/${id}`),
  approve: (id: string) => api.post<Listing>(`/listings/${id}/approve`),
  reject: (id: string, reason: string) => api.post<Listing>(`/listings/${id}/reject`, { reason }),
}

export interface BlogPost {
  id: string  // UUID
  title: string
  slug: string
  excerpt: string
  content: string
  meta_title?: string
  meta_description?: string
  meta_keywords?: string
  category: string
  tags?: string
  author: string
  author_id?: string  // UUID
  status: string
  published_at?: string
  featured: boolean
  featured_image_url?: string
  featured_image_alt?: string
  view_count: number
  read_time_minutes: number
  created_at: string
  updated_at: string
}

export const blog = {
  list: (params?: any) => api.get<BlogPost[]>('/blog', { params }),
  get: (slug: string) => api.get<BlogPost>(`/blog/${slug}`),
  create: (data: any) => api.post<BlogPost>('/blog', data),
  update: (id: string, data: any) => api.patch<BlogPost>(`/blog/${id}`, data),
  publish: (id: string) => api.post<BlogPost>(`/blog/${id}/publish`),
  delete: (id: string) => api.delete(`/blog/${id}`),
}
