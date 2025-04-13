"""
Logo search service for retrieving product logo URLs.

This module provides functionality to search for and retrieve logo URLs for products.
It uses OpenAI API to search for logos and maintains a cache to avoid repeated searches.
"""
import asyncio
import json
import os
import re
from typing import Dict, List, Any, Optional

import requests
from dotenv import load_dotenv
from openai import OpenAI

from app.logging_config import setup_logger

# Get the logger for this module
logger = setup_logger(__name__, "logo_search.log")

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class LogoSearchService:
    """Service for searching and retrieving logo URLs for products."""

    def __init__(
        self, openai_client: Optional[OpenAI] = None, cache_file: Optional[str] = None
    ):
        """
        Initialize the LogoSearchService

        Args:
            openai_client: Optional OpenAI client to use. If not provided, a new one will be created.
            cache_file: Path to the cache file for storing logo URLs. Defaults to 'logo_cache.json'
                      in the current directory.
        """
        self.openai_client = openai_client or OpenAI(api_key=OPENAI_API_KEY)
        self.cache_file = cache_file or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "logo_cache.json"
        )
        self.logo_cache = self._load_cache()
        logger.info("LogoSearchService initialized with cache file: %s", self.cache_file)

    def _load_cache(self) -> Dict[str, str]:
        """
        Load the logo URL cache from the cache file

        Returns:
            dict: Dictionary mapping product names to logo URLs
        """
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    cache = json.load(f)
                logger.info("Loaded %d entries from logo cache", len(cache))
                return cache
            
            logger.info("No logo cache file found, creating new cache")
            return {}
        except (json.JSONDecodeError, IOError) as e:
            logger.error("Error loading logo cache: %s", str(e))
            return {}

    def _save_cache(self) -> None:
        """Save the logo URL cache to the cache file"""
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.logo_cache, f, indent=2)
            logger.info("Saved %d entries to logo cache", len(self.logo_cache))
        except (IOError, TypeError) as e:
            logger.error("Error saving logo cache: %s", str(e))

    def extract_url_from_text(self, text: str) -> str:
        """
        Extract URL from text string

        Args:
            text: Text containing a URL

        Returns:
            str: The extracted URL or empty string if not found
        """
        logger.info("Extracting URL from text: %s...", text[:100])
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        match = re.search(url_pattern, text)
        if match:
            logger.info("Found Logo URL: %s", match.group(0))
            return match.group(0)
        
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
        logger.info("Validating URL: %s", url)
        try:
            # Add a timeout to avoid hanging on slow responses
            response = requests.head(url, timeout=5, allow_redirects=True)
            # Check if status code is in the 2xx range (success)
            is_valid = 200 <= response.status_code < 300
            if is_valid:
                logger.info("URL is valid: %s", url)
            else:
                logger.warning("URL returned status code %d: %s", response.status_code, url)
            return is_valid
        except (requests.RequestException, ValueError) as e:
            # Return False for any request errors or invalid URLs
            logger.error("Error validating URL %s: %s", url, str(e))
            return False

    def get_valid_image_urls(self, urls: List[str]) -> List[str]:
        """
        Filter a list of URLs to only include valid, accessible image URLs

        Args:
            urls: List of URLs to check

        Returns:
            list: List of valid, accessible image URLs
        """
        logger.info("Validating %d URLs", len(urls))
        valid_urls = []
        for url in urls:
            if self.is_valid_url(url) and url.endswith((".png", ".jpg", ".svg")):
                valid_urls.append(url)
        logger.info("Found %d valid URLs out of %d", len(valid_urls), len(urls))
        return valid_urls

    def extract_urls_from_text(self, text: str) -> List[str]:
        """
        Extract all URLs from text string that end with .png, .jpg, or .svg

        Args:
            text: Text containing multiple URLs

        Returns:
            list: List of extracted URLs
        """
        logger.info("Extracting URLs from text: %s...", text[:100])
        # Pattern to match URLs ending with .png, .jpg, or .svg
        url_pattern = r'https?://[^\s<>"]+\.(?:png|svg|jpg)'
        # Find all matches
        matches = re.findall(url_pattern, text)
        logger.info("Found %d URLs matching pattern", len(matches))

        # Remove duplicates while preserving order
        unique_matches = []
        for match in matches:
            if match not in unique_matches:
                unique_matches.append(match)

        logger.info("Found %d unique URLs", len(unique_matches))
        return unique_matches

    async def logo_url(self, product_name: str, _product_website: Optional[str] = None) -> str:
        """
        Search for a logo URL for a product

        Args:
            product_name: Name of the product
            _product_website: Optional website of the product (currently unused)

        Returns:
            str: URL of the product logo
        """
        # Check for partial matches in cache
        product_name_lower = product_name.lower()
        for cache_key in self.logo_cache:
            if (
                product_name_lower in cache_key.lower()
                or cache_key.lower() in product_name_lower
            ):
                cached_url = self.logo_cache[cache_key]
                logger.info(
                    "Using cached logo URL for %s (matched with %s): %s",
                    product_name, cache_key, cached_url
                )
                return cached_url

        if "tools" in product_name:
            if "default" not in self.logo_cache:
                logger.warning("Default logo not found in cache")
                return ""
            return self.logo_cache["default"]

        logger.info("Searching for logo URL for product: %s", product_name)
        query = (
            f"The product is {product_name}, Find the image URL of the product logo ending "
            "with png, jpg, or svg. Just give me the image URL, no additional information."
        )

        try:
            logger.info("Sending query to OpenAI: %s", query)
            response = self.openai_client.responses.create(
                model="gpt-4o-mini",
                input=query,
                tools=[{"type": "web_search"}],
            )

            response_text = response.output[1].content[0].text
            logger.info("Response for %s: %s...", product_name, response_text[:100])

            # Extract URLs from the response
            urls = self.extract_urls_from_text(response_text)

            # If no URLs found with the pattern, try the general URL extraction
            if not urls:
                logger.info(
                    "No URLs found with pattern, trying general extraction for %s",
                    product_name
                )
                url = self.extract_url_from_text(response_text)
                if url:
                    urls = [url]

            # Get valid URLs
            valid_urls = self.get_valid_image_urls(urls)

            # Return the first valid URL or empty string if none found
            result = valid_urls[0] if valid_urls else ""
            logger.info("Final logo URL for %s: %s", product_name, result)

            # Save valid URL to cache
            if result:
                self.logo_cache[product_name] = result
                self._save_cache()
                logger.info("Saved logo URL for %s to cache", product_name)
            elif "default" in self.logo_cache:
                result = self.logo_cache["default"]
                logger.info("No logo URL found for %s, using default logo", product_name)
            else:
                logger.warning(
                    "No logo URL found for %s and no default logo available",
                    product_name
                )
            
            return result
        except Exception as e:  # pylint: disable=broad-except
            # We want to catch all exceptions to prevent API failures from breaking the app
            logger.error("Error searching for logo URL for %s: %s", product_name, str(e))
            return ""

    async def get_logo_urls(self, products: List[Dict[str, Any]]) -> List[str]:
        """
        Get logo URLs for a list of products

        Args:
            products: List of product dictionaries with 'name' and 'website' keys

        Returns:
            list: List of logo URLs
        """
        logger.info("Getting logo URLs for %d products", len(products))
        urls = []
        for i, product in enumerate(products):
            product_name = product.get("name", "")
            product_website = product.get("website_url", "")
            logger.info("Processing product %d/%d: %s", i + 1, len(products), product_name)
            url = await self.logo_url(product_name, product_website)
            urls.append(url)

        logger.info("Logo URLs: number is %d", len(urls))
        return urls

    def reassign_logo_urls(
        self, products: List[Dict[str, Any]], img_urls: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Add logo URLs to the products dictionary

        Args:
            products: Products dictionary
            img_urls: List of logo URLs

        Returns:
            list: Updated products list with logo URLs
        """
        logger.info(
            "Reassigning %d logo URLs to %d products",
            len(img_urls), len(products)
        )
        for i, url in enumerate(img_urls):
            if i < len(products):
                products[i]["logo_url"] = url
                products[i]["image_url"] = products[i].pop("logo_url")
                logger.info("Assigned logo URL to product %d: %s", i + 1, url)
        return products


if __name__ == "__main__":
    service = LogoSearchService()
    test_products = [
        {
            "id": "1",
            "name": "PHP",
            "description": "A widely used server-side scripting language for backend web development.",
            "logo_url": "https://example.com/php.png",
            "website_url": "https://www.php.net/",
        },
        {
            "id": "2",
            "name": "Node.js",
            "description": "A JavaScript runtime built on Chrome's V8 JavaScript engine.",
            "logo_url": "https://example.com/nodejs.png",
            "website_url": "https://nodejs.org/",
        },
    ]
    logo_list = asyncio.run(service.get_logo_urls(test_products))
    updated_products = service.reassign_logo_urls(test_products, logo_list)
    print(updated_products)
