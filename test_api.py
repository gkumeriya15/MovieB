#!/usr/bin/env python3
"""
Test script for MovieBox API endpoints
"""

import asyncio
import httpx
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

async def test_endpoint(url: str, description: str) -> Dict[str, Any]:
    """Test a single endpoint"""
    print(f"Testing URL: {url}")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            result = response.json()
            print(f"✅ {description}: {response.status_code}")
            if result.get("success"):
                print(f"   Data keys: {list(result.get('data', {}).keys())}")
            else:
                print(f"   Error: {result.get('error', 'Unknown error')}")
            return result
    except Exception as e:
        print(f"❌ {description}: {str(e)}")
        return {"success": False, "error": str(e)}

async def test_health():
    """Test health endpoint"""
    return await test_endpoint(f"{BASE_URL}/health", "Health Check")

async def test_search():
    """Test search endpoint"""
    return await test_endpoint(
        f"{BASE_URL}/api/v1/search?q=stranger&type=TV_SERIES&page=1&per_page=5",
        "Search Stranger Things (TV Series)"
    )

async def test_details(search_result=None):
    """Test details endpoint"""
    if search_result and search_result.get("success") and search_result["data"]["items"]:
        item = search_result["data"]["items"][0]
        page_url = item["page_url"]
        return await test_endpoint(
            f"{BASE_URL}/api/v1/details/{page_url}",
            f"Details for {page_url}"
        )
    else:
        # Fallback test
        return await test_endpoint(
            f"{BASE_URL}/api/v1/details/test-page-url",
            "Details for test page URL"
        )

async def test_episodes(search_result=None):
    """Test episodes endpoint"""
    if search_result and search_result.get("success") and search_result["data"]["items"]:
        # Find a TV series
        for item in search_result["data"]["items"]:
            if item["subject_type"] == 2:  # TV_SERIES
                page_url = item["page_url"]
                return await test_endpoint(
                    f"{BASE_URL}/api/v1/episodes/{page_url}",
                    f"Episodes for {page_url}"
                )
    # Fallback test
    return await test_endpoint(
        f"{BASE_URL}/api/v1/episodes/test-page-url",
        "Episodes for test page URL"
    )

async def test_stream():
    """Test stream endpoint with a movie"""
    # Search for a movie specifically
    movie_search = await test_endpoint(
        f"{BASE_URL}/api/v1/search?q=inception&type=MOVIE&page=1&per_page=1",
        "Search for movie to test streaming"
    )
    
    if movie_search.get("success") and movie_search["data"]["items"]:
        item = movie_search["data"]["items"][0]
        page_url = item["page_url"]
        return await test_endpoint(
            f"{BASE_URL}/api/v1/stream/{page_url}",
            f"Stream links for movie {page_url}"
        )
    else:
        # Fallback test
        return await test_endpoint(
            f"{BASE_URL}/api/v1/stream/test-page-url",
            "Stream links for test page URL"
        )

async def main():
    """Run all tests"""
    print("🚀 Testing MovieBox API Endpoints")
    print("=" * 50)

    # Test health
    health_result = await test_health()
    print()

    # Test search
    search_result = await test_search()
    print()

    # Test details
    details_result = await test_details(search_result)
    print()

    # Test episodes
    episodes_result = await test_episodes(search_result)
    print()

    # Test stream
    stream_result = await test_stream()
    print()

    print("🎯 Test Summary:")
    print(f"Health: {'✅' if health_result.get('success') else '❌'}")
    print(f"Search: {'✅' if search_result.get('success') else '❌'}")
    print(f"Details: {'✅' if details_result.get('success') else '❌'}")
    print(f"Episodes: {'✅' if episodes_result.get('success') else '❌'}")
    print(f"Stream: {'✅' if stream_result.get('success') else '❌'}")

if __name__ == "__main__":
    asyncio.run(main())