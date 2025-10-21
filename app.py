from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

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
        # Add headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Step 1: Search for the product on Elipso search page
        search_url = f"https://www.elipso.hr/rezultati/?q={product}"
        search_response = requests.get(search_url, headers=headers, timeout=10)
        search_response.raise_for_status()
        
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
            return jsonify({
                'error': f'No product link found containing "{product}"',
                'search_url': search_url,
                'success': False
            }), 404
        
        # Step 2: Follow the found link and scrape the 2nd <b> tag
        product_response = requests.get(first_link, headers=headers, timeout=10)
        product_response.raise_for_status()
        
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
