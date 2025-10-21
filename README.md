# Elipso Web Scraper

A Flask web scraper that extracts the first `<a>` tag from Elipso product pages.

## Features

- Scrapes product pages from `https://www.elipso.hr/mali-kucanski/usisavaci/`
- Returns the first `<a>` tag found on the page
- RESTful API with JSON responses
- Ready for deployment on Render.com

## Usage

### Local Development

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the application:

```bash
python app.py
```

3. Access the API:

- Home page: `http://localhost:5000/`
- Scrape endpoint: `http://localhost:5000/scrape?product=PRODUCT_CODE`
- Health check: `http://localhost:5000/health`

### API Endpoints

#### GET /

Returns a simple HTML page with usage instructions.

#### GET /scrape?product=PRODUCT_CODE

Scrapes the specified product page and returns the first `<a>` tag.

**Parameters:**

- `product` (required): The product code to scrape

**Example:**

```
GET /scrape?product=PHILIPS-XC3133-01
```

**Response:**

```json
{
  "url": "https://www.elipso.hr/mali-kucanski/usisavaci/PHILIPS-XC3133-01/",
  "first_a_tag": "<a href=\"/some-link\">Link Text</a>",
  "href": "/some-link",
  "text": "Link Text",
  "success": true
}
```

#### GET /health

Returns the health status of the service.

## Deployment on Render.com

1. Push your code to a Git repository (GitHub, GitLab, etc.)
2. Connect your repository to Render.com
3. Create a new Web Service
4. Use the following settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Python Version**: 3.9.0

The `render.yaml` file is included for easy deployment configuration.

## Error Handling

The API handles various error scenarios:

- Missing product parameter
- Network errors
- Invalid URLs
- Pages with no `<a>` tags
- Server errors

All errors return appropriate HTTP status codes and error messages.
