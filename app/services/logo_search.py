import re
import requests
from typing import List, Dict, Any
from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from app.logging_config import setup_logger

# Get the logger for this module
logger = setup_logger(__name__, "logo_search.log")

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class LogoSearchService:
    def __init__(self, openai_client=None, cache_file=None):
        """
        Initialize the LogoSearchService
        
        Args:
            openai_client: Optional OpenAI client to use. If not provided, a new one will be created.
            cache_file: Path to the cache file for storing logo URLs. Defaults to 'logo_cache.json' in the current directory.
        """
        self.openai_client = openai_client or OpenAI(api_key=OPENAI_API_KEY)
        self.cache_file = cache_file or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo_cache.json')
        self.logo_cache = self._load_cache()
        logger.info(f"LogoSearchService initialized with cache file: {self.cache_file}")
    
    def _load_cache(self) -> Dict[str, str]:
        """
        Load the logo URL cache from the cache file
        
        Returns:
            dict: Dictionary mapping product names to logo URLs
        """
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self.logo_cache = json.load(f)
                logger.info(f"Loaded {len(self.logo_cache)} entries from logo cache")
                return self.logo_cache
            else:
                logger.info("No logo cache file found, creating new cache")
                return {}
        except Exception as e:
            logger.error(f"Error loading logo cache: {str(e)}")
            return {}
    
    def _save_cache(self) -> None:
        """
        Save the logo URL cache to the cache file
        """
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.logo_cache, f, indent=2)
            logger.info(f"Saved {len(self.logo_cache)} entries to logo cache")
        except Exception as e:
            logger.error(f"Error saving logo cache: {str(e)}")
    
    def extract_url_from_text(self, text: str) -> str:
        """
        Extract URL from text string
        
        Args:
            text: Text containing a URL
            
        Returns:
            str: The extracted URL or empty string if not found
        """
        logger.info(f"Extracting URL from text: {text[:100]}...")
        # Pattern to match URLs
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        match = re.search(url_pattern, text)
        if match:
            logger.info(f"Found Logo URL: {match.group(0)}")
            return match.group(0)
        else:
            logger.info("No Logo URL Found")
            return ""
    
    def is_valid_url(self, url: str) -> bool:
        """
        Check if a URL is accessible by making a HEAD request
        
        Args:
            url: URL to check
            
        Returns:
            bool: True if URL is accessible, False otherwise
        """
        logger.info(f"Validating URL: {url}")
        try:
            # Add a timeout to avoid hanging on slow responses
            response = requests.head(url, timeout=5, allow_redirects=True)
            # Check if status code is in the 2xx range (success)
            is_valid = 200 <= response.status_code < 300
            if is_valid:
                logger.info(f"URL is valid: {url}")
            else:
                logger.warning(f"URL returned status code {response.status_code}: {url}")
            return is_valid
        except (requests.RequestException, ValueError) as e:
            # Return False for any request errors or invalid URLs
            logger.error(f"Error validating URL {url}: {str(e)}")
            return False
    
    def get_valid_image_urls(self, urls: List[str]) -> List[str]:
        """
        Filter a list of URLs to only include valid, accessible image URLs
        
        Args:
            urls: List of URLs to check
            
        Returns:
            list: List of valid, accessible image URLs
        """
        logger.info(f"Validating {len(urls)} URLs")
        valid_urls = []
        for url in urls:
            if self.is_valid_url(url) and url.endswith(('.png', '.jpg', '.svg')):
                valid_urls.append(url)
        logger.info(f"Found {len(valid_urls)} valid URLs out of {len(urls)}")
        return valid_urls
    
    def extract_urls_from_text(self, text: str) -> List[str]:
        """
        Extract all URLs from text string that end with .png, .jpg, or .svg
        
        Args:
            text: Text containing multiple URLs
            
        Returns:
            list: List of extracted URLs
        """
        logger.info(f"Extracting URLs from text: {text[:100]}...")
        # Pattern to match URLs ending with .png, .jpg, or .svg
        url_pattern = r'https?://[^\s<>"]+\.(?:png|svg|jpg)'
        # Find all matches
        matches = re.findall(url_pattern, text)
        logger.info(f"Found {len(matches)} URLs matching pattern")
        
        # Remove duplicates while preserving order
        unique_matches = []
        for match in matches:
            if match not in unique_matches:
                unique_matches.append(match)
        
        logger.info(f"Found {len(unique_matches)} unique URLs")
        return unique_matches
    
    async def logo_url(self, product_name: str, product_website: str = None) -> str:
        """
        Search for a logo URL for a product
        
        Args:
            product_name: Name of the product
            product_website: Optional website of the product
            
        Returns:
            str: URL of the product logo
        """
        # Check for partial matches in cache
        product_name_lower = product_name.lower()
        for cache_key in self.logo_cache:
            if (product_name_lower in cache_key.lower() or 
                cache_key.lower() in product_name_lower or 
                product_name_lower in cache_key.lower()):
                cached_url = self.logo_cache[cache_key]
                logger.info(f"Using cached logo URL for {product_name} (matched with {cache_key}): {cached_url}")
                return cached_url
        
        if "tools" in product_name:
            if "default" not in self.logo_cache:
                logger.warning("Default logo not found in cache")
                return ""
            return self.logo_cache["default"]
        
        logger.info(f"Searching for logo URL for product: {product_name}, website: {product_website}")
        query = f"The product is {product_name}"
        if product_website:
            query += f", the official website is {product_website}"
        
        query += ", Find the image URL of the product logo ending with png, jpg, or svg. Just give me the image URL, no additional information."
        
        try:
            logger.info(f"Sending query to OpenAI: {query}")
            response = self.openai_client.responses.create(
                model="gpt-4o-mini",
                input=query,
                tools=[{"type": "web_search"}],
            )
            
            response_text = response.output[1].content[0].text
            logger.info(f"Response for {product_name}: {response_text[:100]}...")
            
            # Extract URLs from the response
            urls = self.extract_urls_from_text(response_text)
            
            # If no URLs found with the pattern, try the general URL extraction
            if not urls:
                logger.info(f"No URLs found with pattern, trying general extraction for {product_name}")
                url = self.extract_url_from_text(response_text)
                if url:
                    urls = [url]
            
            # Get valid URLs
            valid_urls = self.get_valid_image_urls(urls)
            
            # Return the first valid URL or empty string if none found
            result = valid_urls[0] if valid_urls else ""
            logger.info(f"Final logo URL for {product_name}: {result}")
            
            # Save valid URL to cache
            if result:
                self.logo_cache[product_name] = result
                self._save_cache()
                logger.info(f"Saved logo URL for {product_name} to cache")
            else:
                if "default" in self.logo_cache:
                    result = self.logo_cache["default"]
                    logger.info(f"No logo URL found for {product_name}, using default logo")
                else:
                    logger.warning(f"No logo URL found for {product_name} and no default logo available")
            return result
        except Exception as e:
            logger.error(f"Error searching for logo URL for {product_name}: {str(e)}")
            return ""
    
    async def get_logo_urls(self, products: List[Dict[str, Any]]) -> List[str]:
        """
        Get logo URLs for a list of products
        
        Args:
            products: List of product dictionaries with 'name' and 'website' keys
            
        Returns:
            list: List of logo URLs
        """
        logger.info(f"Getting logo URLs for {len(products)} products")
        urls = []
        for i, product in enumerate(products):
            product_name = product.get("name", "")
            product_website = product.get("website_url", "")
            logger.info(f"Processing product {i+1}/{len(products)}: {product_name}")
            url = await self.logo_url(product_name, product_website)
            urls.append(url)
        
        logger.info(f"Logo URLs: number is {len(urls)}, urls are {urls}")
        return urls
    
    def reassign_logo_urls(self, products: List[Dict[str, Any]], logo_urls: List[str]) -> Dict[str, Any]:
        """
        Add logo URLs to the products dictionary
        
        Args:
            products: Products dictionary
            logo_urls: List of logo URLs
            
        Returns:
            dict: Updated products dictionary with logo URLs
        """
        logger.info(f"Reassigning {len(logo_urls)} logo URLs to {len(products)} products")
        for i in range(len(products)):
            products[i]["image_url"] = logo_urls[i]
            logger.info(f"Assigned logo URL to product {i+1}: {logo_urls[i]}")
        return products
    

if __name__ == "__main__":
    service = LogoSearchService()
    products = [{"id":"1","name":"PHP","description":"A widely used server-side scripting language for backend web development.","image_url":"https://example.com/php.png","website_url":"https://www.php.net/"},{"id":"2","name":"Node.js","description":"A JavaScript runtime built on Chrome's V8 JavaScript engine, ideal for building APIs and handling real-time data.","image_url":"https://example.com/nodejs.png","website_url":"https://nodejs.org/"},{"id":"3","name":"Express.js","description":"A minimalistic backend framework for Node.js that simplifies building web applications and APIs.","image_url":"https://example.com/express.png","website_url":"https://expressjs.com/"},{"id":"4","name":"Django","description":"A high-level Python web framework that encourages rapid development and clean, pragmatic design.","image_url":"https://example.com/django.png","website_url":"https://www.djangoproject.com/"},{"id":"5","name":"AWS","description":"A comprehensive cloud platform that provides hosting and scaling solutions for applications.","image_url":"https://example.com/aws.png","website_url":"https://aws.amazon.com/"},{"id":"6","name":"ASP.NET Core","description":"A cross-platform framework for building modern, cloud-based, internet-connected applications.","image_url":"https://example.com/aspnetcore.png","website_url":"https://dotnet.microsoft.com/apps/aspnet"},{"id":"7","name":"Spring Boot","description":"A framework that simplifies the setup of new Spring applications, making it easy to create stand-alone, production-grade applications.","image_url":"https://example.com/springboot.png","website_url":"https://spring.io/projects/spring-boot"},{"id":"8","name":"Flask","description":"A lightweight WSGI web application framework in Python, designed for simplicity and flexibility.","image_url":"https://example.com/flask.png","website_url":"https://flask.palletsprojects.com/"},{"id":"9","name":"Ruby on Rails","description":"A server-side web application framework written in Ruby under the MIT License, emphasizing convention over configuration.","image_url":"https://example.com/rails.png","website_url":"https://rubyonrails.org/"},{"id":"10","name":"Laravel","description":"A PHP framework for web artisans, providing an elegant syntax and powerful tools for building applications.","image_url":"https://example.com/laravel.png","website_url":"https://laravel.com/"}]
    import asyncio
    logo_urls = asyncio.run(service.get_logo_urls(products))
    products = service.reassign_logo_urls(products, logo_urls)
    print(products)
