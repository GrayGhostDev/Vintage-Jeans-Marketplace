import { Helmet } from 'react-helmet-async'

interface OrganizationSchemaProps {
  name: string
  url: string
  logo: string
  description: string
  sameAs?: string[]
}

export function OrganizationSchema({ name, url, logo, description, sameAs = [] }: OrganizationSchemaProps) {
  const schema = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name,
    url,
    logo,
    description,
    sameAs,
  }

  return (
    <Helmet>
      <script type="application/ld+json">{JSON.stringify(schema)}</script>
    </Helmet>
  )
}

interface ProductSchemaProps {
  name: string
  description: string
  image: string[]
  brand: string
  offers: {
    price: number
    priceCurrency: string
    availability: 'InStock' | 'OutOfStock' | 'PreOrder'
    url: string
    seller: string
  }
  condition?: 'NewCondition' | 'UsedCondition' | 'RefurbishedCondition'
  category?: string
}

export function ProductSchema({ name, description, image, brand, offers, condition = 'UsedCondition', category }: ProductSchemaProps) {
  const schema = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name,
    description,
    image,
    brand: {
      '@type': 'Brand',
      name: brand,
    },
    offers: {
      '@type': 'Offer',
      ...offers,
      availability: `https://schema.org/${offers.availability}`,
    },
    itemCondition: `https://schema.org/${condition}`,
    ...(category && { category }),
  }

  return (
    <Helmet>
      <script type="application/ld+json">{JSON.stringify(schema)}</script>
    </Helmet>
  )
}

interface BreadcrumbItem {
  name: string
  url: string
}

export function BreadcrumbSchema({ items }: { items: BreadcrumbItem[] }) {
  const schema = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.name,
      item: item.url,
    })),
  }

  return (
    <Helmet>
      <script type="application/ld+json">{JSON.stringify(schema)}</script>
    </Helmet>
  )
}

interface ArticleSchemaProps {
  headline: string
  description: string
  image: string[]
  datePublished: string
  dateModified: string
  author: string
  publisher: {
    name: string
    logo: string
  }
}

export function ArticleSchema({ headline, description, image, datePublished, dateModified, author, publisher }: ArticleSchemaProps) {
  const schema = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline,
    description,
    image,
    datePublished,
    dateModified,
    author: {
      '@type': 'Person',
      name: author,
    },
    publisher: {
      '@type': 'Organization',
      name: publisher.name,
      logo: {
        '@type': 'ImageObject',
        url: publisher.logo,
      },
    },
  }

  return (
    <Helmet>
      <script type="application/ld+json">{JSON.stringify(schema)}</script>
    </Helmet>
  )
}
