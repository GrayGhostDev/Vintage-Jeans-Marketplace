import { Helmet } from 'react-helmet-async'

interface SEOProps {
  title: string
  description: string
  keywords?: string
  canonical?: string
  ogType?: 'website' | 'article' | 'product'
  ogImage?: string
  ogUrl?: string
  twitterCard?: 'summary' | 'summary_large_image'
  noindex?: boolean
}

export default function SEO({
  title,
  description,
  keywords,
  canonical,
  ogType = 'website',
  ogImage = '/og-default.jpg',
  ogUrl,
  twitterCard = 'summary_large_image',
  noindex = false,
}: SEOProps) {
  const siteName = 'Vintage Jeans Marketplace'
  const fullTitle = title.includes(siteName) ? title : `${title} | ${siteName}`
  const url = ogUrl || (typeof window !== 'undefined' ? window.location.href : '')

  return (
    <Helmet>
      {/* Primary Meta Tags */}
      <title>{fullTitle}</title>
      <meta name="title" content={fullTitle} />
      <meta name="description" content={description} />
      {keywords && <meta name="keywords" content={keywords} />}
      {canonical && <link rel="canonical" href={canonical} />}
      {noindex && <meta name="robots" content="noindex,nofollow" />}

      {/* Open Graph / Facebook */}
      <meta property="og:type" content={ogType} />
      <meta property="og:url" content={url} />
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={ogImage} />
      <meta property="og:site_name" content={siteName} />

      {/* Twitter */}
      <meta property="twitter:card" content={twitterCard} />
      <meta property="twitter:url" content={url} />
      <meta property="twitter:title" content={fullTitle} />
      <meta property="twitter:description" content={description} />
      <meta property="twitter:image" content={ogImage} />
    </Helmet>
  )
}
