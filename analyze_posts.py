"""
Example script to read and analyze scraped Danbooru posts.
Demonstrates memory-efficient processing of JSONL files.
"""

import json
from collections import Counter
from datetime import datetime


def count_posts(filename="danbooru_posts.jsonl"):
    """Count total number of posts in the file."""
    count = 0
    with open(filename, 'r', encoding='utf-8') as f:
        for _ in f:
            count += 1
    return count


def get_post_by_id(post_id, filename="danbooru_posts.jsonl"):
    """Find and return a specific post by ID."""
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            post = json.loads(line)
            if post['id'] == post_id:
                return post
    return None


def analyze_file_ratings(filename="danbooru_posts.jsonl", sample_size=None):
    """Analyze the distribution of post ratings."""
    rating_counter = Counter()
    count = 0
    
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            post = json.loads(line)
            rating = post.get('rating', 'unknown')
            rating_counter[rating] += 1
            count += 1
            
            if sample_size and count >= sample_size:
                break
    
    print(f"\nRating Distribution (from {count} posts):")
    print("-" * 40)
    for rating, count in rating_counter.most_common():
        percentage = (count / sum(rating_counter.values())) * 100
        print(f"{rating}: {count} ({percentage:.2f}%)")


def get_top_tags(filename="danbooru_posts.jsonl", top_n=20, sample_size=None):
    """Get the most common tags from posts."""
    tag_counter = Counter()
    count = 0
    
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            post = json.loads(line)
            
            # Combine all tag types
            all_tags = []
            if 'tag_string' in post:
                all_tags = post['tag_string'].split()
            else:
                # Fallback: combine individual tag categories
                all_tags.extend(post.get('tag_string_general', '').split())
                all_tags.extend(post.get('tag_string_character', '').split())
                all_tags.extend(post.get('tag_string_copyright', '').split())
                all_tags.extend(post.get('tag_string_artist', '').split())
                all_tags.extend(post.get('tag_string_meta', '').split())
            
            tag_counter.update(all_tags)
            count += 1
            
            if sample_size and count >= sample_size:
                break
    
    print(f"\nTop {top_n} Tags (from {count} posts):")
    print("-" * 40)
    for tag, count in tag_counter.most_common(top_n):
        print(f"{tag}: {count}")


def filter_posts_by_tags(tags, filename="danbooru_posts.jsonl", output_file="filtered_posts.jsonl"):
    """Filter posts that contain ALL specified tags."""
    tags_set = set(tags)
    matched_count = 0
    
    with open(filename, 'r', encoding='utf-8') as infile:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for line in infile:
                post = json.loads(line)
                
                # Get all tags from the post
                post_tags = set()
                if 'tag_string' in post:
                    post_tags = set(post['tag_string'].split())
                else:
                    post_tags.update(post.get('tag_string_general', '').split())
                    post_tags.update(post.get('tag_string_character', '').split())
                    post_tags.update(post.get('tag_string_copyright', '').split())
                    post_tags.update(post.get('tag_string_artist', '').split())
                    post_tags.update(post.get('tag_string_meta', '').split())
                
                # Check if all required tags are present
                if tags_set.issubset(post_tags):
                    outfile.write(line)
                    matched_count += 1
    
    print(f"\nFiltered {matched_count} posts with tags: {tags}")
    print(f"Saved to: {output_file}")


def get_date_range(filename="danbooru_posts.jsonl"):
    """Get the date range of posts in the file."""
    dates = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            post = json.loads(line)
            created_at = post.get('created_at')
            if created_at:
                dates.append(created_at)
    
    if dates:
        print(f"\nDate Range:")
        print("-" * 40)
        print(f"Earliest: {min(dates)}")
        print(f"Latest: {max(dates)}")
        print(f"Total posts: {len(dates)}")


def show_sample_post(filename="danbooru_posts.jsonl"):
    """Display a sample post to see available fields."""
    with open(filename, 'r', encoding='utf-8') as f:
        line = f.readline()
        if line:
            post = json.loads(line)
            print("\nSample Post Structure:")
            print("-" * 40)
            print(json.dumps(post, indent=2))
            print("\nAvailable Fields:")
            print(", ".join(post.keys()))


def main():
    """Main function demonstrating various analysis options."""
    import os
    
    filename = "danbooru_posts.jsonl"
    
    # Check if file exists
    if not os.path.exists(filename):
        print(f"Error: {filename} not found!")
        print("Please run the scraper first to generate data.")
        return
    
    print("=" * 50)
    print("Danbooru Post Analysis")
    print("=" * 50)
    
    # Basic statistics
    try:
        total = count_posts(filename)
        print(f"\nTotal posts in file: {total}")
    except Exception as e:
        print(f"Error counting posts: {e}")
        return
    
    # Show a sample post structure (first post only)
    print("\n" + "=" * 50)
    try:
        show_sample_post(filename)
    except Exception as e:
        print(f"Error showing sample: {e}")
    
    # Analyze ratings (sample first 10,000 posts for speed)
    print("\n" + "=" * 50)
    try:
        analyze_file_ratings(filename, sample_size=10000)
    except Exception as e:
        print(f"Error analyzing ratings: {e}")
    
    # Get top tags (sample first 10,000 posts for speed)
    print("\n" + "=" * 50)
    try:
        get_top_tags(filename, top_n=20, sample_size=10000)
    except Exception as e:
        print(f"Error analyzing tags: {e}")
    
    # Get date range
    print("\n" + "=" * 50)
    try:
        # Note: This reads all dates, could be slow for large files
        # Consider sampling if file is too large
        get_date_range(filename)
    except Exception as e:
        print(f"Error getting date range: {e}")
    
    print("\n" + "=" * 50)
    print("Analysis complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
