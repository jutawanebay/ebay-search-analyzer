import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple
import time
import random
import re

def extract_price(price_elem) -> float:
    """Extract and normalize price from price element"""
    try:
        if not price_elem:
            return None
        # Remove currency symbols and convert to float
        price_text = price_elem.get_text().strip()
        # Extract numbers including decimal points
        price_match = re.search(r'[\d,]+\.\d{2}', price_text)
        if price_match:
            # Remove commas and convert to float
            return float(price_match.group().replace(',', ''))
        return None
    except Exception:
        return None

def scrape_ebay_results(url: str) -> Tuple[List[str], List[float]]:
    """
    Scrape product titles and prices from eBay search results

    Args:
        url: eBay search URL

    Returns:
        Tuple of (list of product titles, list of prices)
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }

    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            # Add parameters to show 60 items per page if not present
            if '_ipg=' not in url:
                url += '&_ipg=60' if '?' in url else '?_ipg=60'

            # Add random delay between retries
            if attempt > 0:
                time.sleep(retry_delay + random.uniform(1, 3))

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all product titles and prices
            titles = []
            prices = []

            # Get all item containers
            items = soup.select('.s-item__wrapper')

            for item in items:
                # Extract title
                title_elem = item.select_one('.s-item__title')
                if title_elem and 'Shop on eBay' not in title_elem.text:
                    titles.append(title_elem.text.strip())

                    # Extract price
                    price_elem = item.select_one('.s-item__price')
                    price = extract_price(price_elem)
                    prices.append(price)

            # Limit to first 60 results
            return titles[:60], prices[:60]

        except requests.RequestException as e:
            if attempt == max_retries - 1:  # Last attempt
                raise Exception(f"Failed to fetch eBay results after {max_retries} attempts: {str(e)}")
            continue  # Try again
        except Exception as e:
            raise Exception(f"Error processing eBay page: {str(e)}")