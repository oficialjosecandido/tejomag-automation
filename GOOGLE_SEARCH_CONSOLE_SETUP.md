# Google Search Console Setup Guide

This guide will help you get your article pages indexed on Google Search Console.

## ✅ What's Already Configured

1. **SEO Meta Tags** - All article pages have:
   - Dynamic page titles
   - Meta descriptions
   - Open Graph tags (for social sharing)
   - Twitter Card tags
   - JSON-LD structured data (NewsArticle schema)
   - Canonical URLs

2. **robots.txt** - Created at `https://tejomag.pt/robots.txt`
   - Allows all search engines to crawl
   - Points to sitemap location

3. **Sitemap** - Dynamic XML sitemap available at:
   - `https://tejomag-backend.azurewebsites.net/sitemap.xml`
   - Includes all articles with slugs
   - Updates automatically as new articles are added

## 📋 Steps to Index Your Articles

### Step 1: Verify Your Property in Google Search Console

1. Go to [Google Search Console](https://search.google.com/search-console)
2. Click **"Add Property"**
3. Enter your domain: `https://tejomag.pt`
4. Choose verification method:
   - **Recommended**: HTML file upload
   - **Alternative**: HTML tag (add to `frontend/public/index.html`)
   - **Alternative**: DNS record (add TXT record to your DNS)

### Step 2: Submit Your Sitemap

1. After verification, go to **Sitemaps** in the left menu
2. Enter your sitemap URL:
   ```
   https://tejomag-backend.azurewebsites.net/sitemap.xml
   ```
3. Click **"Submit"**

**Note**: Google will automatically discover new articles from the sitemap and index them.

### Step 3: Request Indexing for Important Pages (Optional)

1. Go to **URL Inspection** tool
2. Enter a specific article URL, e.g.:
   ```
   https://tejomag.pt/article/your-article-slug
   ```
3. Click **"Request Indexing"**

This is optional since the sitemap will handle most indexing automatically.

### Step 4: Monitor Indexing Status

1. Go to **Coverage** report to see:
   - How many pages are indexed
   - Any indexing errors
   - Pages that need attention

2. Go to **Performance** report to see:
   - Search queries
   - Click-through rates
   - Average position in search results

## 🔍 SEO Features Already Implemented

### Article Pages Include:

- ✅ **Dynamic Title**: `{Article Title} | TejoMag`
- ✅ **Meta Description**: First 160 characters of article content
- ✅ **Canonical URL**: Prevents duplicate content issues
- ✅ **Open Graph Tags**: For Facebook, LinkedIn sharing
- ✅ **Twitter Cards**: For Twitter sharing
- ✅ **Structured Data**: JSON-LD NewsArticle schema
- ✅ **Mobile-Friendly**: Responsive design
- ✅ **Fast Loading**: Optimized images and content

### Structured Data (JSON-LD)

Each article includes structured data in this format:

```json
{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "headline": "Article Title",
  "description": "Article description",
  "image": "Article image URL",
  "author": {
    "@type": "Organization",
    "name": "BBC/Le Monde/El Pais"
  },
  "publisher": {
    "@type": "Organization",
    "name": "TejoMag"
  },
  "datePublished": "2024-01-01T00:00:00Z",
  "dateModified": "2024-01-01T00:00:00Z",
  "articleSection": "Category",
  "inLanguage": "pt-PT"
}
```

## 🚀 Best Practices

1. **Regular Content Updates**: New articles are automatically added to the sitemap
2. **Unique Slugs**: Each article has a unique, SEO-friendly slug
3. **Quality Content**: Articles are translated and well-formatted
4. **Internal Linking**: Articles link back to homepage
5. **External Links**: Articles link to original sources (good for SEO)

## 📊 Monitoring

After submitting your sitemap, you should see:

- **Within 24-48 hours**: Google starts crawling your pages
- **Within 1-2 weeks**: Pages start appearing in search results
- **Ongoing**: New articles are automatically discovered and indexed

## 🔧 Troubleshooting

### Pages Not Indexing

1. **Check robots.txt**: Make sure it's not blocking crawlers
2. **Check sitemap**: Verify sitemap is accessible and valid
3. **Check page quality**: Ensure pages load quickly and have good content
4. **Check for errors**: Look in Coverage report for any errors

### Sitemap Errors

- If you see sitemap errors, check:
  - Backend is running and accessible
  - Sitemap XML is valid (check at `https://tejomag-backend.azurewebsites.net/sitemap.xml`)
  - All URLs in sitemap are accessible

### Slow Indexing

- Google typically indexes pages within 1-2 weeks
- New sites may take longer
- Ensure you have quality, unique content
- Submit important pages manually for faster indexing

## 📝 Additional Resources

- [Google Search Console Help](https://support.google.com/webmasters)
- [Google's SEO Starter Guide](https://developers.google.com/search/docs/beginner/seo-starter-guide)
- [Structured Data Testing Tool](https://search.google.com/test/rich-results)

## 🎯 Next Steps

1. ✅ Verify your property in Google Search Console
2. ✅ Submit your sitemap
3. ✅ Monitor indexing status
4. ✅ Optimize based on performance data

Your articles should start appearing in Google search results within 1-2 weeks!

