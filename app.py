from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
import time
import random

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>Elipso Web Scraper</h1>
    <p>Usage: GET /scrape?product=PRODUCT_CODE</p>
    <p>Example: <a href="/scrape?product=PHILIPS-XC3133-01">/scrape?product=PHILIPS-XC3133-01</a></p>
    <p>This will scrape: https://www.elipso.hr/mali-kucanski/usisavaci/PRODUCT_CODE/</p>
    """

@app.route('/scrape')
def scrape():
    product = request.args.get('product')
    
    if not product:
        return jsonify({'error': 'Product parameter is required'}), 400
    
    try:
        # Rotate between different user agents to avoid detection
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        # Add comprehensive headers to mimic a real browser and avoid blocking
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,hr;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.google.com/'
        }
        
        # Create a session to maintain cookies and connection
        session = requests.Session()
        session.headers.update(headers)
        
        # Step 1: First visit the main page to establish a session
        try:
            main_page = session.get("https://www.elipso.hr/", timeout=10)
            main_page.raise_for_status()
        except:
            pass  # Continue even if main page fails
        
        # Step 2: Search for the product on Elipso search page
        time.sleep(random.uniform(1, 3))  # Random delay to appear more human-like
        search_url = f"https://www.elipso.hr/rezultati/?q={product}"
        
        # Try multiple approaches if the first one fails
        search_response = None
        for attempt in range(3):
            try:
                search_response = session.get(search_url, timeout=15)
                search_response.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                if attempt < 2:  # Not the last attempt
                    time.sleep(random.uniform(2, 5))  # Wait before retry
                    # Update headers for retry
                    session.headers.update({'User-Agent': random.choice(user_agents)})
                else:
                    raise e
        
        # Parse the search results
        search_soup = BeautifulSoup(search_response.content, 'html.parser')
        
        # Find the first <a> tag with href containing the search value
        first_link = None
        for a_tag in search_soup.find_all('a'):
            href = a_tag.get('href', '')
            if product.lower() in href.lower():
                first_link = href
                break
        
        if not first_link:
            # Try alternative approach - direct product URL construction
            try:
                # Try common product URL patterns
                alternative_urls = [
                    f"https://www.elipso.hr/mali-kucanski/usisavaci/{product}/",
                    f"https://www.elipso.hr/mali-kucanski/usisavaci/{product.upper()}/",
                    f"https://www.elipso.hr/mali-kucanski/usisavaci/{product.lower()}/",
                ]
                
                for alt_url in alternative_urls:
                    try:
                        alt_response = session.get(alt_url, timeout=10)
                        if alt_response.status_code == 200:
                            first_link = alt_url
                            break
                    except:
                        continue
                
                if not first_link:
                    return jsonify({
                        'error': f'No product link found containing "{product}"',
                        'search_url': search_url,
                        'success': False
                    }), 404
            except:
                return jsonify({
                    'error': f'No product link found containing "{product}"',
                    'search_url': search_url,
                    'success': False
                }), 404
        
        # Step 3: Follow the found link and scrape the 2nd <b> tag
        time.sleep(random.uniform(1, 2))  # Random delay to appear more human-like
        
        # Try to get the product page with retry logic
        product_response = None
        for attempt in range(3):
            try:
                product_response = session.get(first_link, timeout=15)
                product_response.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                if attempt < 2:  # Not the last attempt
                    time.sleep(random.uniform(2, 4))
                    # Update headers for retry
                    session.headers.update({'User-Agent': random.choice(user_agents)})
                else:
                    raise e
        
        # Parse the product page
        product_soup = BeautifulSoup(product_response.content, 'html.parser')
        
        # Find all <b> tags
        all_b_tags = product_soup.find_all('b')
        
        if len(all_b_tags) >= 2:
            # Return the 2nd <b> tag
            second_b_tag = all_b_tags[1]  # Index 1 for the 2nd element
            result = {
                'search_url': search_url,
                'product_url': first_link,
                'second_b_tag': str(second_b_tag),
                'text': second_b_tag.get_text(strip=True),
                'success': True
            }
        elif len(all_b_tags) == 1:
            result = {
                'search_url': search_url,
                'product_url': first_link,
                'second_b_tag': None,
                'message': 'Only 1 <b> tag found, need at least 2',
                'success': False
            }
        else:
            result = {
                'search_url': search_url,
                'product_url': first_link,
                'second_b_tag': None,
                'message': 'No <b> tags found on the product page',
                'success': False
            }
            
        return jsonify(result)
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': f'Failed to fetch the page: {str(e)}',
            'success': False
        }), 500
    except Exception as e:
        return jsonify({
            'error': f'An error occurred: {str(e)}',
            'success': False
        }), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
