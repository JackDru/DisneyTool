print("Elias scraper starting...")

import requests
import time
import os
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

print("Supabase connected.")

# ── Subreddits ────────────────────────────────────────────────────────────────
SUBREDDITS = [
    "WaltDisneyWorld",
    "DisneyWorld",
    "DisneyParks",
    "Disneyland",
]

# ── 60 search terms ───────────────────────────────────────────────────────────
SEARCH_TERMS = [
    # Operational failures
    "broken",
    "not working",
    "wait time",
    "line was",
    "cast member",
    "they closed",
    "shut down",
    "out of order",
    "understaffed",
    "no one helped",
    "queue",
    "boarding group",
    # Pricing and value
    "not worth",
    "too expensive",
    "price increase",
    "Genie+",
    "genie plus"
    "Genie plus"
    "lightning lane",
    "used to be free",
    "cost too much",
    "overpriced",
    "nickel and dimed",
    "paid extra",
    # Suggestions and feedback
    "they should",
    "they need a"
    "they need to"
    "wish disney",
    "bring back",
    "why did disney",
    "used to be",
    "needs to fix",
    "would be better if",
    "suggestion",
    "feedback",
    "please add",
    # Sentiment and experience
    "disappointed",
    "last time",
    "never again",
    "first time",
    "compared to",
    "universal does",
    "going downhill",
    "not the same",
    "miss the old",
    "noticed that",
    "ruined",
    "used to love",
    # Specific systems and areas
    "mobile order",
    "park reservation",
    "my disney experience",
    "rope drop",
    "early entry",
    "after hours",
    "dining reservation",
    "hotel check in",
    "bus wait",
    "monorail",
    # Strategic and pattern observations
    "disney keeps",
    "every time I go",
    "pattern of",
    "they removed",
    "corporate decision",
    "feels different",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

def get_existing_urls():
    """Pull all comment URLs already in DB for deduplication."""
    try:
        result = supabase.table("raw_comments")\
            .select("comment_url")\
            .execute()
        return set(r['comment_url'] for r in result.data if r.get('comment_url'))
    except Exception as e:
        print(f"Warning: could not load existing URLs: {e}")
        return set()

def search_posts(subreddit, term, limit=5):
    """Search a subreddit for posts matching a term from the past week."""
    url = (
        f"https://www.reddit.com/r/{subreddit}/search.json"
        f"?q={requests.utils.quote(term)}"
        f"&restrict_sr=1"
        f"&sort=relevance"
        f"&t=week"
        f"&limit={limit}"
    )
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return []
        data = r.json()
        posts = data.get('data', {}).get('children', [])
        return [p['data'] for p in posts if p.get('data')]
    except Exception as e:
        print(f"  Search error [{subreddit} / {term}]: {e}")
        return []

def get_comments(post, subreddit):
    """Fetch all comments for a given post."""
    post_id  = post.get('id', '')
    url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json?limit=200&depth=3"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return []
        data = r.json()
        if not isinstance(data, list) or len(data) < 2:
            return []
        return extract_comments(data[1]['data']['children'], post)
    except Exception as e:
        print(f"  Comment fetch error [{post_id}]: {e}")
        return []

def extract_comments(children, post, depth=0):
    """Recursively extract comments from Reddit JSON tree."""
    comments = []
    post_id    = post.get('id', '')
    post_title = post.get('title', '')
    subreddit  = post.get('subreddit', '')
    post_url   = f"https://www.reddit.com{post.get('permalink', '')}"

    for child in children:
        if not isinstance(child, dict):
            continue
        kind = child.get('kind', '')
        data = child.get('data', {})

        if kind == 't1':
            body = data.get('body', '').strip()
            if (
                not body
                or body == '[deleted]'
                or body == '[removed]'
                or len(body) < 30
            ):
                continue

            comment_id  = data.get('id', '')
            comment_url = f"https://www.reddit.com{data.get('permalink', '')}"
            upvotes     = data.get('score', 0) or 0
            created_utc = data.get('created_utc', 0)
            username    = data.get('author', '')

            if created_utc:
                date_posted = datetime.fromtimestamp(
                    created_utc, tz=timezone.utc
                ).isoformat()
            else:
                date_posted = None

            comments.append({
                'source':         'reddit',
                'username':       username,
                'date_posted':    date_posted,
                'content':        body,
                'upvotes':        upvotes,
                'subreddit':      subreddit,
                'post_id':        post_id,
                'post_title':     post_title,
                'url':            post_url,
                'comment_url':    comment_url,
                'comment_length': len(body),
                'processed':      False,
            })

            # Recurse into replies
            replies = data.get('replies', '')
            if isinstance(replies, dict):
                reply_children = replies.get('data', {}).get('children', [])
                if reply_children:
                    comments.extend(
                        extract_comments(reply_children, post, depth + 1)
                    )

    return comments

def save_comments(comments, existing_urls):
    """Insert new comments, skip duplicates."""
    new_count = 0
    for c in comments:
        if c['comment_url'] in existing_urls:
            continue
        try:
            supabase.table("raw_comments").insert(c).execute()
            existing_urls.add(c['comment_url'])
            new_count += 1
        except Exception as e:
            print(f"  Insert error: {e}")
    return new_count

def run():
    existing_urls = get_existing_urls()
    print(f"Loaded {len(existing_urls)} existing comments for deduplication\n")

    total_saved   = 0
    total_posts   = 0
    seen_post_ids = set()

    combos = len(SUBREDDITS) * len(SEARCH_TERMS)
    combo_count = 0

    for subreddit in SUBREDDITS:
        print(f"\n{'='*50}")
        print(f"Subreddit: r/{subreddit}")
        print(f"{'='*50}")

        for term in SEARCH_TERMS:
            combo_count += 1
            pct = round((combo_count / combos) * 100, 1)
            print(f"\n[{pct}%] Searching: \"{term}\"")

            posts = search_posts(subreddit, term, limit=5)

            if not posts:
                print(f"  No posts found")
                time.sleep(1)
                continue

            new_posts = [p for p in posts if p.get('id') not in seen_post_ids]
            for p in new_posts:
                seen_post_ids.add(p.get('id'))

            print(f"  {len(new_posts)} new posts (skipped {len(posts)-len(new_posts)} duplicates)")

            for post in new_posts:
                total_posts += 1
                title = post.get('title', '')[:60]
                print(f"  → \"{title}\"")

                comments = get_comments(post, subreddit)
                saved    = save_comments(comments, existing_urls)
                total_saved += saved
                print(f"    {len(comments)} comments fetched, {saved} new saved")

                time.sleep(1.5)

            time.sleep(1)

    print(f"\n{'='*50}")
    print(f"SCRAPE COMPLETE")
    print(f"Posts processed:  {total_posts}")
    print(f"Comments saved:   {total_saved}")
    print(f"{'='*50}")

run()
