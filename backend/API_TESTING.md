# 🧪 Vintage Jeans API - Testing Guide

Complete API testing examples for all endpoints using cURL, HTTPie, and REST Client formats.

## 📋 Table of Contents

1. [Setup](#setup)
2. [Health Check](#health-check)
3. [Seller Authentication](#seller-authentication)
4. [Seller Management](#seller-management)
5. [Listings Management](#listings-management)
6. [Blog Management](#blog-management)
7. [Testing Scripts](#testing-scripts)

---

## Setup

### Environment Variables

```bash
# Development
export API_URL="http://localhost:8000/api"

# Production
export API_URL="https://your-app.onrender.com/api"

# Store token after login
export TOKEN="your-jwt-token-here"
```

---

## Health Check

### cURL

```bash
# Check API health
curl -X GET ${API_URL:-http://localhost:8000/api}/health | jq

# Expected Response:
# {
#   "status": "ok",
#   "service": "vintage-jeans-api",
#   "version": "2.0.0",
#   "database": {
#     "status": "ok",
#     "database": "supabase",
#     "connected": true
#   }
# }
```

### HTTPie

```bash
http GET ${API_URL:-http://localhost:8000/api}/health
```

---

## Seller Authentication

### 1. Register New Seller

#### cURL

```bash
curl -X POST ${API_URL:-http://localhost:8000/api}/sellers/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "securePassword123",
    "full_name": "John Doe",
    "business_name": "Vintage Denim Co",
    "phone": "+1-555-0123",
    "location": "Los Angeles, CA",
    "referred_by_code": null
  }' | jq
```

#### HTTPie

```bash
http POST ${API_URL:-http://localhost:8000/api}/sellers/register \
  email="john.doe@example.com" \
  password="securePassword123" \
  full_name="John Doe" \
  business_name="Vintage Denim Co" \
  phone="+1-555-0123" \
  location="Los Angeles, CA"
```

#### Expected Response

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john.doe@example.com",
  "full_name": "John Doe",
  "business_name": "Vintage Denim Co",
  "location": "Los Angeles, CA",
  "is_verified": false,
  "role": "seller",
  "total_listings": 0,
  "active_listings": 0,
  "referral_code": "VJ12345678",
  "created_at": "2025-11-03T20:30:00"
}
```

### 2. Login

#### cURL

```bash
# Login and save token
RESPONSE=$(curl -X POST ${API_URL:-http://localhost:8000/api}/sellers/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john.doe@example.com&password=securePassword123")

# Extract token
export TOKEN=$(echo $RESPONSE | jq -r '.access_token')
echo "Token: $TOKEN"
```

#### HTTPie

```bash
http --form POST ${API_URL:-http://localhost:8000/api}/sellers/login \
  username="john.doe@example.com" \
  password="securePassword123"
```

#### Expected Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "seller": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john.doe@example.com",
    "full_name": "John Doe",
    "location": "Los Angeles, CA",
    "is_verified": false,
    "role": "seller",
    "total_listings": 0,
    "active_listings": 0,
    "referral_code": "VJ12345678",
    "created_at": "2025-11-03T20:30:00"
  }
}
```

---

## Seller Management

### 1. Get Current Seller Profile

#### cURL

```bash
curl -X GET ${API_URL:-http://localhost:8000/api}/sellers/me \
  -H "Authorization: Bearer ${TOKEN}" | jq
```

#### HTTPie

```bash
http GET ${API_URL:-http://localhost:8000/api}/sellers/me \
  "Authorization: Bearer ${TOKEN}"
```

### 2. Update Profile

#### cURL

```bash
curl -X PATCH ${API_URL:-http://localhost:8000/api}/sellers/me \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John D. Doe",
    "business_name": "Premium Vintage Denim",
    "phone": "+1-555-9999",
    "location": "San Francisco, CA"
  }' | jq
```

#### HTTPie

```bash
http PATCH ${API_URL:-http://localhost:8000/api}/sellers/me \
  "Authorization: Bearer ${TOKEN}" \
  full_name="John D. Doe" \
  business_name="Premium Vintage Denim" \
  phone="+1-555-9999" \
  location="San Francisco, CA"
```

### 3. List All Sellers (Admin Only)

#### cURL

```bash
curl -X GET "${API_URL:-http://localhost:8000/api}/sellers/all?skip=0&limit=10" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" | jq
```

### 4. Verify Seller (Admin Only)

#### cURL

```bash
curl -X PATCH ${API_URL:-http://localhost:8000/api}/sellers/{seller_id}/verify \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" | jq
```

---

## Listings Management

### 1. Create New Listing

#### cURL

```bash
curl -X POST ${API_URL:-http://localhost:8000/api}/listings \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Vintage Levis 501 - 1990s Stonewash",
    "description": "Classic Levis 501 jeans from the 1990s in excellent condition. Original stonewash finish with minimal fading. These jeans have been professionally cleaned and are ready to wear.",
    "brand": "Levis",
    "decade": "1990s",
    "year": 1995,
    "model": "501",
    "waist_size": 32,
    "inseam_length": 32,
    "size_label": "32x32",
    "condition": "excellent",
    "price": 85.00,
    "currency": "USD",
    "purchase_price": 25.00,
    "primary_image_url": "https://example.com/images/levis-501-front.jpg",
    "image_urls": [
      "https://example.com/images/levis-501-front.jpg",
      "https://example.com/images/levis-501-back.jpg",
      "https://example.com/images/levis-501-tag.jpg"
    ]
  }' | jq
```

#### HTTPie

```bash
http POST ${API_URL:-http://localhost:8000/api}/listings \
  "Authorization: Bearer ${TOKEN}" \
  title="Vintage Levis 501 - 1990s Stonewash" \
  description="Classic Levis 501 jeans..." \
  brand="Levis" \
  condition="excellent" \
  price:=85.00 \
  waist_size:=32 \
  inseam_length:=32
```

### 2. List All Listings

#### cURL

```bash
# List with pagination
curl -X GET "${API_URL:-http://localhost:8000/api}/listings?skip=0&limit=20" \
  -H "Authorization: Bearer ${TOKEN}" | jq

# Filter by platform
curl -X GET "${API_URL:-http://localhost:8000/api}/listings?platform=manual&skip=0&limit=20" \
  -H "Authorization: Bearer ${TOKEN}" | jq

# Filter by status
curl -X GET "${API_URL:-http://localhost:8000/api}/listings?status_filter=active&skip=0&limit=20" \
  -H "Authorization: Bearer ${TOKEN}" | jq

# Filter by brand
curl -X GET "${API_URL:-http://localhost:8000/api}/listings?brand=Levis&skip=0&limit=20" \
  -H "Authorization: Bearer ${TOKEN}" | jq
```

#### HTTPie

```bash
# Basic list
http GET ${API_URL:-http://localhost:8000/api}/listings \
  "Authorization: Bearer ${TOKEN}" \
  skip==0 \
  limit==20

# With filters
http GET ${API_URL:-http://localhost:8000/api}/listings \
  "Authorization: Bearer ${TOKEN}" \
  platform=="manual" \
  status_filter=="active" \
  brand=="Levis"
```

### 3. Get Listing by ID

#### cURL

```bash
curl -X GET ${API_URL:-http://localhost:8000/api}/listings/{listing_id} \
  -H "Authorization: Bearer ${TOKEN}" | jq
```

### 4. Update Listing

#### cURL

```bash
curl -X PATCH ${API_URL:-http://localhost:8000/api}/listings/{listing_id} \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Vintage Levis 501 - 1990s Stonewash (Updated)",
    "price": 95.00,
    "condition": "excellent"
  }' | jq
```

### 5. Delete Listing

#### cURL

```bash
curl -X DELETE ${API_URL:-http://localhost:8000/api}/listings/{listing_id} \
  -H "Authorization: Bearer ${TOKEN}"
```

### 6. Approve Listing (Admin Only)

#### cURL

```bash
curl -X POST ${API_URL:-http://localhost:8000/api}/listings/{listing_id}/approve \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" | jq
```

### 7. Reject Listing (Admin Only)

#### cURL

```bash
curl -X POST ${API_URL:-http://localhost:8000/api}/listings/{listing_id}/reject \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Insufficient image quality. Please upload higher resolution images."
  }' | jq
```

---

## Blog Management

### 1. List Blog Posts (Public)

#### cURL

```bash
# List all published posts
curl -X GET "${API_URL:-http://localhost:8000/api}/blog?skip=0&limit=20" | jq

# Filter by category
curl -X GET "${API_URL:-http://localhost:8000/api}/blog?category=selling_tips&skip=0&limit=20" | jq

# Filter by featured
curl -X GET "${API_URL:-http://localhost:8000/api}/blog?featured=true&skip=0&limit=20" | jq
```

#### HTTPie

```bash
http GET ${API_URL:-http://localhost:8000/api}/blog \
  skip==0 \
  limit==20 \
  category=="selling_tips" \
  featured==true
```

### 2. Get Blog Post by Slug (Public)

#### cURL

```bash
curl -X GET ${API_URL:-http://localhost:8000/api}/blog/how-to-sell-vintage-jeans-online | jq
```

### 3. Create Blog Post (Admin Only)

#### cURL

```bash
curl -X POST ${API_URL:-http://localhost:8000/api}/blog \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "How to Sell Vintage Jeans Online in 2025",
    "slug": "how-to-sell-vintage-jeans-online-2025",
    "excerpt": "Complete guide to selling vintage denim online with maximum ROI",
    "content": "# Introduction\n\nSelling vintage jeans online has become increasingly profitable...",
    "meta_title": "How to Sell Vintage Jeans Online | 2025 Guide",
    "meta_description": "Learn how to sell vintage jeans for top dollar. Expert tips on pricing, platforms, and finding buyers who pay premium for rare Levi'\''s.",
    "meta_keywords": "sell vintage jeans, how to sell vintage denim, vintage jeans pricing",
    "featured_image_url": "https://example.com/blog/vintage-jeans-hero.jpg",
    "featured_image_alt": "Stack of vintage Levi'\''s 501 jeans",
    "category": "selling_tips",
    "tags": "pricing,online-selling,levis,denim",
    "read_time_minutes": 8,
    "related_posts": null,
    "related_listings": null
  }' | jq
```

### 4. Update Blog Post (Admin Only)

#### cURL

```bash
curl -X PATCH ${API_URL:-http://localhost:8000/api}/blog/{post_id} \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "How to Sell Vintage Jeans Online in 2025 (Updated)",
    "excerpt": "Updated complete guide with new marketplace data",
    "featured": true
  }' | jq
```

### 5. Publish Blog Post (Admin Only)

#### cURL

```bash
curl -X POST ${API_URL:-http://localhost:8000/api}/blog/{post_id}/publish \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" | jq
```

### 6. Delete Blog Post (Admin Only)

#### cURL

```bash
curl -X DELETE ${API_URL:-http://localhost:8000/api}/blog/{post_id} \
  -H "Authorization: Bearer ${ADMIN_TOKEN}"
```

---

## Testing Scripts

### Complete Flow Test (Bash)

Save as `test_api.sh`:

```bash
#!/bin/bash
set -e

API_URL="${API_URL:-http://localhost:8000/api}"

echo "🧪 Testing Vintage Jeans API"
echo "API URL: $API_URL"
echo ""

# Health Check
echo "1. Testing Health Check..."
curl -s ${API_URL}/health | jq -r '.status' | grep -q "ok" && echo "✅ Health check passed" || echo "❌ Health check failed"
echo ""

# Register Seller
echo "2. Registering new seller..."
REGISTER_RESPONSE=$(curl -s -X POST ${API_URL}/sellers/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test'$(date +%s)'@example.com",
    "password": "testPassword123",
    "full_name": "Test Seller",
    "location": "Test City"
  }')

SELLER_ID=$(echo $REGISTER_RESPONSE | jq -r '.id')
echo "✅ Seller registered with ID: $SELLER_ID"
echo ""

# Login
echo "3. Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST ${API_URL}/sellers/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test'$(date +%s)'@example.com&password=testPassword123")

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
echo "✅ Login successful, token: ${TOKEN:0:20}..."
echo ""

# Get Profile
echo "4. Getting seller profile..."
curl -s ${API_URL}/sellers/me \
  -H "Authorization: Bearer $TOKEN" | jq -r '.email' | grep -q "@" && echo "✅ Profile retrieved" || echo "❌ Profile failed"
echo ""

# Create Listing
echo "5. Creating listing..."
CREATE_LISTING=$(curl -s -X POST ${API_URL}/listings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Vintage Jeans",
    "description": "Test description",
    "brand": "TestBrand",
    "condition": "good",
    "price": 50.00
  }')

LISTING_ID=$(echo $CREATE_LISTING | jq -r '.id')
echo "✅ Listing created with ID: $LISTING_ID"
echo ""

# List Listings
echo "6. Listing all listings..."
curl -s "${API_URL}/listings?skip=0&limit=10" \
  -H "Authorization: Bearer $TOKEN" | jq -r 'length' | grep -qE '[0-9]+' && echo "✅ Listings retrieved" || echo "❌ Listings failed"
echo ""

# Delete Listing
echo "7. Deleting listing..."
curl -s -X DELETE ${API_URL}/listings/${LISTING_ID} \
  -H "Authorization: Bearer $TOKEN" && echo "✅ Listing deleted" || echo "❌ Delete failed"
echo ""

echo "✅ All tests completed successfully!"
```

Make executable and run:

```bash
chmod +x test_api.sh
./test_api.sh
```

### JavaScript/Fetch Example

```javascript
const API_URL = process.env.VITE_API_URL || 'http://localhost:8000/api'

// Register
async function registerSeller() {
  const response = await fetch(`${API_URL}/sellers/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: 'john@example.com',
      password: 'password123',
      full_name: 'John Doe',
      location: 'Los Angeles, CA'
    })
  })
  return response.json()
}

// Login
async function login(email, password) {
  const response = await fetch(`${API_URL}/sellers/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username: email, password })
  })
  const data = await response.json()
  localStorage.setItem('token', data.access_token)
  return data
}

// Get Profile
async function getProfile() {
  const token = localStorage.getItem('token')
  const response = await fetch(`${API_URL}/sellers/me`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  return response.json()
}

// Create Listing
async function createListing(listingData) {
  const token = localStorage.getItem('token')
  const response = await fetch(`${API_URL}/listings`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(listingData)
  })
  return response.json()
}

// List Listings
async function getListings(params = {}) {
  const token = localStorage.getItem('token')
  const queryString = new URLSearchParams(params).toString()
  const response = await fetch(`${API_URL}/listings?${queryString}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  return response.json()
}
```

---

## REST Client File Format

Save as `api.http` for use with VS Code REST Client extension:

```http
### Variables
@baseUrl = http://localhost:8000/api
@token = your-token-here
@listingId = listing-uuid-here

### Health Check
GET {{baseUrl}}/health

### Register Seller
POST {{baseUrl}}/sellers/register
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "location": "Los Angeles, CA"
}

### Login
# @name login
POST {{baseUrl}}/sellers/login
Content-Type: application/x-www-form-urlencoded

username=john@example.com&password=password123

### Get Profile
GET {{baseUrl}}/sellers/me
Authorization: Bearer {{token}}

### Create Listing
POST {{baseUrl}}/listings
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "title": "Vintage Levis 501",
  "description": "Classic jeans",
  "brand": "Levis",
  "condition": "excellent",
  "price": 85.00,
  "waist_size": 32,
  "inseam_length": 32
}

### List Listings
GET {{baseUrl}}/listings?skip=0&limit=20
Authorization: Bearer {{token}}

### Get Listing by ID
GET {{baseUrl}}/listings/{{listingId}}
Authorization: Bearer {{token}}

### Update Listing
PATCH {{baseUrl}}/listings/{{listingId}}
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "title": "Updated Title",
  "price": 95.00
}

### Delete Listing
DELETE {{baseUrl}}/listings/{{listingId}}
Authorization: Bearer {{token}}

### List Blog Posts
GET {{baseUrl}}/blog?skip=0&limit=20

### Get Blog Post by Slug
GET {{baseUrl}}/blog/how-to-sell-vintage-jeans-online
```

---

## Tips & Best Practices

### 1. Store Tokens Securely

```bash
# Don't hardcode tokens in scripts
# Use environment variables or secret management
export TOKEN=$(security find-generic-password -w -s "vintage-jeans-token")
```

### 2. Pretty Print JSON

```bash
# Use jq for formatted output
curl ... | jq

# Or python's json.tool
curl ... | python -m json.tool
```

### 3. Handle Errors

```bash
# Check HTTP status code
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" ${API_URL}/health)
if [ $HTTP_CODE -eq 200 ]; then
  echo "Success"
else
  echo "Failed with code: $HTTP_CODE"
fi
```

### 4. Automated Testing

Consider using:
- **Postman**: For collections and automated testing
- **Newman**: CLI runner for Postman collections
- **pytest**: Python testing framework (see next section)
- **Jest/Vitest**: JavaScript testing for frontend

---

## Next Steps

1. **Run Manual Tests**: Execute the cURL commands to verify endpoints
2. **Set Up Automated Tests**: Use pytest for backend API tests
3. **Create Postman Collection**: Import REST Client file into Postman
4. **Monitor Performance**: Track API response times in production
5. **Set Up CI/CD**: Automate testing in your deployment pipeline

Happy Testing! 🧪✅
