#!/usr/bin/env python3
"""
Test script for the amazon tool.
"""
import asyncio
import os
import sys
from dotenv import load_dotenv
from serpapi import SerpApiClient as SerpApiSearch

# Add the parent directory to the path so we can import from server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()
API_KEY = os.getenv("SERPAPI_API_KEY")

async def test_amazon_tool():
    """Test the amazon function logic directly"""
    print("🛒 Testing amazon tool functionality...")
    
    # Test parameters
    params = {
        "k": "Coffee",
        "amazon_domain": "amazon.com",
        "language": "en_US",
        "device": "desktop"
    }
    
    print(f"📝 Test parameters: {params}")
    
    # Add API key and engine (same as in the actual function)
    params = {
        "api_key": API_KEY,
        "engine": "amazon",
        **params
    }
    
    try:
        # This mirrors the exact logic from the amazon function
        search = SerpApiSearch(params)
        data = search.get_dict()

        if not data:
            result = {"organic_results": [], "product_ads": {}, "search_metadata": {}, "search_parameters": params, "error": "No response from SerpApi."}
        else:
            result = {
                "organic_results": data.get("organic_results", []),
                "product_ads": data.get("product_ads", {}),
                "search_metadata": data.get("search_metadata", {}),
                "search_parameters": data.get("search_parameters", params),
                "search_information": data.get("search_information", {})
            }
        
        print(f"✅ Function executed successfully!")
        print(f"📊 Response keys: {list(result.keys())}")
        
        if "error" in result:
            print(f"❌ Error in response: {result['error']}")
            return False
            
        organic_results = result.get("organic_results", [])
        product_ads = result.get("product_ads", {})
        search_info = result.get("search_information", {})
        
        print(f"📦 Found {len(organic_results)} organic results")
        print(f"📢 Product ads available: {'Yes' if product_ads else 'No'}")
        print(f"🔍 Total results: {search_info.get('total_results', 'N/A')}")
        
        if organic_results or product_ads:
            print("✅ Amazon function returns product data properly!")
            
            # Show sample product info
            if organic_results:
                first_product = organic_results[0]
                print(f"☕ Sample product: {first_product.get('title', 'N/A')}")
                print(f"💰 Price: {first_product.get('price', 'N/A')}")
                print(f"⭐ Rating: {first_product.get('rating', 'N/A')}")
                print(f"📝 Reviews: {first_product.get('reviews', 'N/A')}")
                if "asin" in first_product:
                    print(f"🆔 ASIN: {first_product['asin']}")
            
            # Show product ads info if available
            if product_ads and "products" in product_ads:
                ad_products = product_ads["products"]
                if ad_products:
                    print(f"📢 Found {len(ad_products)} sponsored products")
                    first_ad = ad_products[0]
                    print(f"📢 Sample ad: {first_ad.get('title', 'N/A')}")
            
            # Show metadata
            metadata = result.get("search_metadata", {})
            print(f"🔍 Search ID: {metadata.get('id', 'N/A')}")
            print(f"📈 Status: {metadata.get('status', 'N/A')}")
            
            return True
        else:
            print("❌ No products found in response")
            print(f"Available data keys: {list(data.keys()) if 'data' in locals() else 'No data'}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_amazon_tool())
    print(f"\n{'✅ AMAZON TEST PASSED' if success else '❌ AMAZON TEST FAILED'}")