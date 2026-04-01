"""
Test script for Episode Streaming API with token expiration handling
"""

import asyncio
import sys
from app.utils.stream_helpers import URLNormalizer, EpisodeParser, StreamTokenExpiration
from app.utils.stream_cache import StreamCache
import time


def test_url_normalizer():
    """Test URL normalization functionality"""
    print("=" * 60)
    print("Testing URL Normalizer")
    print("=" * 60)
    
    test_cases = [
        {
            "input": "https://moviebox.ph/detail/boyfriend-on-demand-hindi-OXFhFpXHnc6?id=5203417860348986440",
            "expected_slug": "boyfriend-on-demand-hindi-OXFhFpXHnc6",
            "expected_subject_id": "5203417860348986440",
        },
        {
            "input": "/detail/boyfriend-on-demand-hindi-OXFhFpXHnc6?id=5203417860348986440",
            "expected_slug": "boyfriend-on-demand-hindi-OXFhFpXHnc6",
            "expected_subject_id": "5203417860348986440",
        },
        {
            "input": "detail/boyfriend-on-demand-hindi-OXFhFpXHnc6?id=5203417860348986440",
            "expected_slug": "boyfriend-on-demand-hindi-OXFhFpXHnc6",
            "expected_subject_id": "5203417860348986440",
        },
        {
            "input": "5203417860348986440",
            "expected_slug": "5203417860348986440",
            "expected_subject_id": "5203417860348986440",
        },
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        result = URLNormalizer.normalize_full_url(test_case["input"])
        
        print(f"\nTest {i}: {test_case['input'][:50]}...")
        print(f"  Valid: {result['valid']}")
        print(f"  Slug: {result['slug']}")
        print(f"  Subject ID: {result['subject_id']}")
        
        assert result["valid"], f"Test {i} failed: URL should be valid"
        assert result["slug"] == test_case["expected_slug"], f"Test {i} failed: slug mismatch"
        assert result["subject_id"] == test_case["expected_subject_id"], f"Test {i} failed: subject_id mismatch"
        print(f"  ✅ PASSED")
    
    print("\n✅ ALL URL NORMALIZER TESTS PASSED")


def test_episode_parser():
    """Test episode ID parsing"""
    print("\n" + "=" * 60)
    print("Testing Episode Parser")
    print("=" * 60)
    
    test_cases = [
        {"input": "s1e1", "expected_season": 1, "expected_episode": 1},
        {"input": "s2e5", "expected_season": 2, "expected_episode": 5},
        {"input": "s10e12", "expected_season": 10, "expected_episode": 12},
        {"input": "S1E1", "expected_season": 1, "expected_episode": 1},  # Case insensitive
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        result = EpisodeParser.parse_episode_id(test_case["input"])
        
        print(f"\nTest {i}: {test_case['input']}")
        assert result is not None, f"Test {i} failed: parsing returned None"
        print(f"  Season: {result['season']}, Episode: {result['episode']}")
        
        assert result["season"] == test_case["expected_season"], f"Test {i} failed: season mismatch"
        assert result["episode"] == test_case["expected_episode"], f"Test {i} failed: episode mismatch"
        print(f"  ✅ PASSED")
    
    # Test invalid formats
    invalid_cases = ["invalid", "1x2", "episode1", "s1-e2"]
    print("\nTesting invalid formats:")
    for invalid in invalid_cases:
        result = EpisodeParser.parse_episode_id(invalid)
        assert result is None, f"Invalid format '{invalid}' should return None"
        print(f"  '{invalid}': ✅ correctly returned None")
    
    print("\n✅ ALL EPISODE PARSER TESTS PASSED")


def test_token_expiration():
    """Test token expiration detection"""
    print("\n" + "=" * 60)
    print("Testing Token Expiration Detection")
    print("=" * 60)
    
    current_time = int(time.time())
    
    # Create test URLs
    test_cases = [
        {
            "name": "Valid stream (expires in 24 hours)",
            "url": f"https://example.com/video.mp4?sign=abc123&t={current_time + 86400}",
            "should_be_expired": False,
        },
        {
            "name": "Expired stream (expired 1 hour ago)",
            "url": f"https://example.com/video.mp4?sign=abc123&t={current_time - 3600}",
            "should_be_expired": True,
        },
        {
            "name": "About to expire (in 1 minute)",
            "url": f"https://example.com/video.mp4?sign=abc123&t={current_time + 60}",
            "should_be_expired": True,  # Because of 5-minute buffer
        },
        {
            "name": "No expiration token",
            "url": "https://example.com/video.mp4?sign=abc123",
            "should_be_expired": False,
        },
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        is_expired = StreamTokenExpiration.is_expired(test_case["url"])
        remaining = StreamTokenExpiration.get_remaining_validity_seconds(test_case["url"])
        
        print(f"\nTest {i}: {test_case['name']}")
        print(f"  Expired: {is_expired}")
        print(f"  Remaining: {remaining}s")
        
        assert is_expired == test_case["should_be_expired"], \
            f"Test {i} failed: expiration status mismatch"
        print(f"  ✅ PASSED")
    
    print("\n✅ ALL TOKEN EXPIRATION TESTS PASSED")


def test_stream_cache():
    """Test stream cache functionality"""
    print("\n" + "=" * 60)
    print("Testing Stream Cache")
    print("=" * 60)
    
    cache = StreamCache(default_ttl_seconds=2)  # Short TTL for testing
    
    # Test basic set/get
    print("\nTest 1: Basic cache operations")
    cache_key = StreamCache._generate_key("episode", "test-slug", "123456", 1, 1)
    test_data = {"streams": [{"url": "test"}]}
    
    cache.set(cache_key, test_data)
    retrieved = cache.get(cache_key)
    
    assert retrieved == test_data, "Retrieved data doesn't match stored data"
    print(f"  ✅ Stored and retrieved data successfully")
    
    # Test cache expiration
    print("\nTest 2: Cache expiration")
    retrieved = cache.get(cache_key)
    assert retrieved is not None, "Cache should still be valid"
    print(f"  ✅ Cache is valid immediately after storage")
    
    time.sleep(2.5)
    retrieved = cache.get(cache_key)
    assert retrieved is None, "Cache should have expired"
    print(f"  ✅ Cache correctly expired after TTL")
    
    # Test cache invalidation
    print("\nTest 3: Manual cache invalidation")
    cache.set(cache_key, test_data, ttl_seconds=10)
    invalidated = cache.invalidate(cache_key)
    assert invalidated, "Invalidation should return True"
    retrieved = cache.get(cache_key)
    assert retrieved is None, "Cache should be empty after invalidation"
    print(f"  ✅ Cache invalidation works correctly")
    
    # Test pattern-based invalidation
    print("\nTest 4: Pattern-based invalidation")
    cache.set(StreamCache._generate_key("episode", "test-slug", "123456", 1, 1), test_data, ttl_seconds=10)
    cache.set(StreamCache._generate_key("episode", "test-slug", "123456", 1, 2), test_data, ttl_seconds=10)
    cache.set(StreamCache._generate_key("episode", "test-slug", "123456", 2, 1), test_data, ttl_seconds=10)
    
    # invalidate all episodes of season 1
    count = cache.invalidate_by_pattern("episode:test-slug:123456:1:*")
    assert count == 2, f"Should have invalidated 2 entries, got {count}"
    print(f"  ✅ Pattern-based invalidation removed {count} entries")
    
    # Test cache stats
    print("\nTest 5: Cache statistics")
    stats = cache.get_stats()
    print(f"  Total entries: {stats['total_entries']}")
    print(f"  Active entries: {stats['active_entries']}")
    print(f"  ✅ Cache stats retrieved successfully")
    
    print("\n✅ ALL STREAM CACHE TESTS PASSED")


def test_episode_mapping():
    """Test episode ID to episode mapping"""
    print("\n" + "=" * 60)
    print("Testing Episode Mapping")
    print("=" * 60)
    
    seasons_data = [
        {
            "season_number": 1,
            "episode_count": 3,
            "episodes": [
                {"id": "s1e1", "title": "Pilot", "episode_number": 1},
                {"id": "s1e2", "title": "Episode 2", "episode_number": 2},
                {"id": "s1e3", "title": "Episode 3", "episode_number": 3},
            ]
        },
        {
            "season_number": 2,
            "episode_count": 2,
            "episodes": [
                {"id": "s2e1", "title": "Season 2 Premier", "episode_number": 1},
                {"id": "s2e2", "title": "Season 2 Episode 2", "episode_number": 2},
            ]
        }
    ]
    
    episode_map = EpisodeParser.create_episode_map(seasons_data)
    
    print(f"\nCreated episode map with {len(episode_map)} episodes")
    
    # Verify all episodes are mapped
    expected_ids = ["s1e1", "s1e2", "s1e3", "s2e1", "s2e2"]
    for episode_id in expected_ids:
        assert episode_id in episode_map, f"Episode {episode_id} not found in map"
        print(f"  ✅ {episode_id}: {episode_map[episode_id]['title']}")
    
    print("\n✅ ALL EPISODE MAPPING TESTS PASSED")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("MovieBox Episode Streaming API - Test Suite")
    print("=" * 60)
    
    try:
        test_url_normalizer()
        test_episode_parser()
        test_token_expiration()
        test_stream_cache()
        test_episode_mapping()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
