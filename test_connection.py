"""
Test script to verify Danbooru API connectivity and basic functionality.
Run this before starting the full scraper to ensure everything works.
"""

import requests
import json
import sys


def test_api_connection():
    """Test basic API connectivity."""
    print("Testing Danbooru API connection...")
    
    try:
        url = "https://danbooru.donmai.us/posts.json"
        params = {'limit': 1}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        posts = response.json()
        
        if posts and len(posts) > 0:
            print("✓ API connection successful!")
            print(f"  Latest post ID: {posts[0]['id']}")
            return True
        else:
            print("✗ API returned no posts")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Connection error - check your internet connection")
        return False
    except requests.exceptions.Timeout:
        print("✗ Request timed out - server may be slow")
        return False
    except requests.exceptions.HTTPError as e:
        print(f"✗ HTTP error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_id_range_query():
    """Test ID range query functionality."""
    print("\nTesting ID range query...")
    
    try:
        url = "https://danbooru.donmai.us/posts.json"
        params = {
            'tags': 'id:1..100',
            'limit': 10
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        posts = response.json()
        
        if posts:
            print(f"✓ ID range query successful!")
            print(f"  Retrieved {len(posts)} posts")
            print(f"  Post IDs: {[p['id'] for p in posts[:5]]}")
            return True
        else:
            print("✗ No posts returned for ID range query")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_post_structure():
    """Test and display post data structure."""
    print("\nTesting post data structure...")
    
    try:
        url = "https://danbooru.donmai.us/posts.json"
        params = {'limit': 1}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        posts = response.json()
        
        if posts and len(posts) > 0:
            post = posts[0]
            print("✓ Sample post retrieved!")
            print(f"\n  Available fields ({len(post.keys())} total):")
            
            # Display key fields
            important_fields = [
                'id', 'created_at', 'updated_at', 'uploader_id',
                'score', 'rating', 'image_width', 'image_height',
                'tag_string', 'tag_count', 'file_url', 'large_file_url',
                'preview_file_url', 'source', 'md5', 'file_ext', 'file_size'
            ]
            
            for field in important_fields:
                if field in post:
                    value = post[field]
                    if isinstance(value, str) and len(value) > 50:
                        value = value[:50] + "..."
                    print(f"    - {field}: {value}")
            
            print(f"\n  All fields: {', '.join(sorted(post.keys()))}")
            return True
        else:
            print("✗ No posts returned")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_pagination():
    """Test pagination functionality."""
    print("\nTesting pagination...")
    
    try:
        url = "https://danbooru.donmai.us/posts.json"
        
        # Fetch page 1
        params = {'limit': 5, 'page': 1}
        response1 = requests.get(url, params=params, timeout=10)
        response1.raise_for_status()
        posts1 = response1.json()
        
        # Fetch page 2
        params = {'limit': 5, 'page': 2}
        response2 = requests.get(url, params=params, timeout=10)
        response2.raise_for_status()
        posts2 = response2.json()
        
        if posts1 and posts2:
            print(f"✓ Pagination working!")
            print(f"  Page 1: {len(posts1)} posts, IDs: {[p['id'] for p in posts1]}")
            print(f"  Page 2: {len(posts2)} posts, IDs: {[p['id'] for p in posts2]}")
            
            # Check for overlap (there shouldn't be any)
            ids1 = set(p['id'] for p in posts1)
            ids2 = set(p['id'] for p in posts2)
            overlap = ids1 & ids2
            
            if overlap:
                print(f"  ⚠ Warning: Found overlapping IDs: {overlap}")
            else:
                print(f"  ✓ No overlap between pages")
            
            return True
        else:
            print("✗ Pagination test failed")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def estimate_total_posts():
    """Estimate total number of posts available."""
    print("\nEstimating total posts...")
    
    try:
        url = "https://danbooru.donmai.us/posts.json"
        params = {'limit': 1, 'page': 1}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        posts = response.json()
        
        if posts:
            highest_id = posts[0]['id']
            print(f"✓ Highest post ID: {highest_id:,}")
            print(f"  Estimated scraping time (at 200 posts/sec with 1s delay):")
            
            hours = (highest_id / 200) / 3600
            days = hours / 24
            
            print(f"    ~{hours:.1f} hours ({days:.1f} days)")
            print(f"  Estimated file size (rough): {(highest_id * 2) / 1024:.1f} MB")
            
            return True
        else:
            print("✗ Could not estimate")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Danbooru API Scraper - Connection Test")
    print("=" * 60)
    
    tests = [
        ("API Connection", test_api_connection),
        ("ID Range Query", test_id_range_query),
        ("Post Structure", test_post_structure),
        ("Pagination", test_pagination),
        ("Total Posts Estimate", estimate_total_posts),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! You're ready to run the scraper.")
        print("  Run: python scraper.py")
        return 0
    else:
        print("\n✗ Some tests failed. Please check your connection and try again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
