# 👖 Vintage Jeans Platform – Market Research Data Workflow (Updated)

## Stage 1 – Focus Area: User-Listed Vintage & Slightly-Used Jeans Marketplace

### 🎯 Objective
To create a **platform** where users can list slightly used and vintage jeans for resale, allowing other customers to browse, purchase, and discover niche denim pieces.

### 🧩 Research Questions
- Who are the **target audiences**?  
  - Vintage denim collectors, sustainable fashion buyers, casual thrifters, resellers.  
- What **listing details** define value?  
  - Brand, decade, condition, wash, fit, provenance, material, unique features.  
- What **platform experiences** do users expect?  
  - Ease of listing, discovery algorithms, trust/seller reputation, eco-impact metrics.  
- Which **niche opportunities** exist?  
  - Localized vintage jean communities, recycled/upcycled denim, AI-assisted sizing, or authenticity verification.

### 🧭 Outcome
These focus points guide your data collection, API research, and eventual product positioning.

---

## Stage 2 – Data Acquisition (Including Developer Portals / APIs)

The goal here is to **collect relevant data** from existing resale marketplaces to understand trends, listings, and user behavior.  
This helps benchmark your upcoming platform against established ones.

### 📊 Target Platforms and Developer Portal Access

| Platform | Developer Access | API/CLI Availability | Notes / Limitations |
|-----------|------------------|----------------------|---------------------|
| **Whatnot** | ✅ Yes | GraphQL API + Webhooks | Developer portal live (https://developers.whatnot.com). Seller API in preview mode, limited access. OAuth 2.0 supported. |
| **eBay** | ✅ Yes | REST + GraphQL API | Extensive dev portal (https://developer.ebay.com). Offers item search, listings, pricing, trends, and affiliate data. |
| **Etsy** | ✅ Yes | REST API + OAuth | (https://developers.etsy.com). Supports product listings, categories, analytics, and shop metadata. |
| **Depop** | ⚠️ No Public API | CLI unofficial / limited | Public API deprecated. Some unofficial endpoints exist; scraping must comply with terms. |
| **Poshmark** | ⚠️ No Public API | CLI unofficial | No official API. Limited data via scraping. |
| **Grailed** | ⚠️ Partial API | Unofficial JSON endpoints | GraphQL endpoints observed but undocumented; access subject to change. |
| **Google Trends** | ✅ Yes | Trends API (pytrends) | Useful for search volume and geo-interest analysis. |
| **Social (Instagram / Threads)** | ✅ Partial | Meta Graph API | Use hashtags or mentions to track engagement trends. |

---

### 🗂️ Data Pipeline

**Raw Data Sources**
- Marketplace APIs (listings, prices, seller ratings)
- Trend APIs (Google Trends, social hashtags)
- Fashion blogs / forums (unstructured text)
- Internal survey data (user feedback from beta testers)

**Storage Locations**
```
data/
├── raw/          # Unfiltered API or scraped data
├── processed/    # Cleaned, normalized, deduplicated data
└── insights/     # Final reports, AI summaries
```

---

### ⚙️ Developer Access Steps

1. **Register for API Keys** where available:
   - eBay, Etsy, Whatnot (if access opens)
2. **Define Extraction Scope**
   - Data type: listings, categories, sold history, pricing trends
   - Frequency: hourly/daily sync
3. **Implement Collectors**
   - Use Python scripts or CLI tools for API ingestion
   - For non-API platforms, consider legal web scraping or partner data feeds
4. **Store to SQLite / PostgreSQL**
   - Schema example:
     ```
     TABLE listings (
       id INTEGER PRIMARY KEY,
       platform TEXT,
       title TEXT,
       brand TEXT,
       decade TEXT,
       price FLOAT,
       location TEXT,
       condition TEXT,
       created_at DATETIME
     )
     ```

---

### 🧮 AI Integration

When a dataset is uploaded via `/research/upload`, GPT-5 will:
- Identify key **listing trends**
- Summarize **market opportunities**
- Flag **data gaps** or **emerging subcultures** (e.g., Y2K denim surge)
- Suggest **feature directions** for the new platform

---

### 🪶 Example Upload Command
```bash
curl -X POST http://127.0.0.1:8000/research/upload   -F "client_name=Vintage Jeans Marketplace Research"   -F "file=@data/processed/ebay_vintage_listings.csv"
```

---

### 🔄 Next Steps
1. Verify Whatnot API access — request Developer Preview participation.  
2. Register for eBay and Etsy APIs; begin collecting vintage denim listings.  
3. Build lightweight Python data collectors (`/collectors/ebay_collector.py`, `/collectors/etsy_collector.py`).  
4. Begin AI analysis cycle:  
   - Upload → Summarize → Compare → Visualize.  
5. Store insights to `/reports/insights/` and use them to guide MVP feature design.

---

### 🧠 Optional Expansion
Add a **CLI agent** in your repo for manual runs:
```bash
python cli_research.py --source ebay --keywords "vintage jeans" --days 30
```

That agent can pipe results directly into your FastAPI app for automatic summarization.
