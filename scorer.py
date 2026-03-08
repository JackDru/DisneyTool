print("Elias scorer starting...")

import openai
from supabase import create_client
from dotenv import load_dotenv
import os
import json
import time

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

print("All connected.")

SUBREDDIT_MAP = {
    "WaltDisneyWorld":      "WDW",
    "DisneyWorld":          "WDW",
    "WDW":                  "WDW",
    "GalacticStarcruiser":  "WDW",
    "MagicKingdom":         "WDW",
    "EPCOT":                "WDW",
    "HollywoodStudios":     "WDW",
    "AnimalKingdom":        "WDW",
    "DisneySprings":        "WDW",
    "WDWPlanning":          "WDW",
    "Disneyland":           "DL",
    "CaliforniaAdventure":  "DL",
    "DisneylandResort":     "DL",
    "DCA":                  "DL",
    "DisneyCruiseLife":     "Cruises",
    "DCL":                  "Cruises",
    "DisneyCruise":         "Cruises",
    "DisneyResorts":        "Hotels",
    "DisneyVacationClub":   "Hotels",
    "DVC":                  "Hotels",
    "disneyparks":          None,
    "disney":               None,
    "DisneyPlanning":       None,
    "StarWars":             None,
    "saltierthancrait":     None,
    "videos":               None,
    "blankies":             None,
    "news":                 None,
    "television":           None,
    "entertainment":        None,
}

PROJECT_KEYWORDS = {
    "Galactic Starcruiser": [
        "starcruiser", "star cruiser", "galactic starcruiser",
        "halcyon", "star wars hotel", "starcruiser hotel",
        "$6000", "$5000", "two night", "2 night stay",
        "immersive hotel", "larp hotel"
    ],
    "Galaxy's Edge": [
        "galaxy's edge", "galaxys edge", "batuu",
        "rise of the resistance", "rise of resistance",
        "smuggler's run", "smugglers run", "millennium falcon",
        "black spire", "star wars land"
    ],
    "Tron Lightcycle Run": [
        "tron", "lightcycle", "tron ride", "tron coaster"
    ],
    "Guardians Coaster": [
        "guardians", "guardians of the galaxy", "cosmic rewind",
        "epcot coaster", "guardians coaster"
    ],
    "Remy's Ratatouille": [
        "remy", "ratatouille", "rat ride", "france pavilion ride"
    ],
    "Haunted Mansion": [
        "haunted mansion", "doom buggy", "ghost host",
        "stretching room", "999 happy haunts"
    ],
    "Space Mountain": [
        "space mountain", "space mtn"
    ],
    "EPCOT": [
        "epcot", "world showcase", "future world",
        "international festival", "flower and garden",
        "food and wine", "festival of the arts"
    ],
    "Magic Kingdom": [
        "magic kingdom", "mk ", " mk,", "main street usa",
        "cinderella castle", "cinderella's castle",
        "fantasyland", "tomorrowland", "adventureland",
        "frontierland", "liberty square"
    ],
    "Hollywood Studios": [
        "hollywood studios", "dhs", "tower of terror",
        "slinky dog", "toy story land", "indiana jones stunt",
        "muppet vision"
    ],
    "Animal Kingdom": [
        "animal kingdom", "ak ", " ak,", "avatar",
        "pandora", "flight of passage", "na'vi river",
        "expedition everest", "kilimanjaro safari"
    ],
    "Genie+": [
        "genie+", "genie plus", "lightning lane",
        "individual lightning lane", "fastpass",
        "fast pass", "virtual queue", "boarding group"
    ],
    "My Disney Experience": [
        "my disney experience", "mde", "disney app",
        "mobile order", "mobile ordering", "park pass",
        "park reservation"
    ],
    "Disneyland Park": [
        "disneyland park", "anaheim", "matterhorn",
        "new orleans square", "critter country",
        "indiana jones adventure"
    ],
    "California Adventure": [
        "california adventure", "dca", "carsland",
        "cars land", "radiator springs", "web slingers",
        "avengers campus", "soarin", "incredicoaster",
        "buena vista street"
    ],
    "Disney Cruise Line": [
        "disney cruise", "dcl", "disney wish", "disney fantasy",
        "disney dream", "disney magic", "disney wonder",
        "castaway cay", "disney treasure", "cruise ship",
        "stateroom", "rotational dining"
    ],
    "Grand Floridian": [
        "grand floridian", "grand flo", "gf resort"
    ],
    "Polynesian Resort": [
        "polynesian", "poly resort", "disney polynesian"
    ],
    "Wilderness Lodge": [
        "wilderness lodge", "fort wilderness"
    ],
    "Disney Hotels": [
        "disney resort hotel", "disney hotel", "disney resort",
        "value resort", "moderate resort", "deluxe resort",
        "vacation club", "dvc resort"
    ],
}

def assign_project_tags(content, post_title):
    text = (content + " " + post_title).lower()
    tags = []
    for project, keywords in PROJECT_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            tags.append(project)
    return tags if tags else ["General Disney"]

def infer_experience(subreddit, content, post_title):
    mapped = SUBREDDIT_MAP.get(subreddit)
    if mapped is not None:
        return mapped
    text = (content + " " + post_title).lower()
    if any(w in text for w in ["disneyland", "california adventure", "anaheim", "dca"]):
        return "DL"
    if any(w in text for w in ["cruise", "dcl", "disney wish", "castaway"]):
        return "Cruises"
    if any(w in text for w in ["grand floridian", "polynesian", "wilderness lodge",
                                "boardwalk inn", "yacht club", "beach club",
                                "art of animation", "pop century", "all star"]):
        return "Hotels"
    if any(w in text for w in ["disney world", "wdw", "orlando", "magic kingdom",
                                "epcot", "animal kingdom", "hollywood studios",
                                "starcruiser", "halcyon", "galaxy's edge",
                                "batuu", "tron", "guardians"]):
        return "WDW"
    return "WDW"


# ── PASS 1: Quality filter ────────────────────────────────────────────────────

def filter_batch(comments):
    """Pass 1: Identify which comments contain genuine actionable intelligence.
    No upvote bias — purely quality-based."""

    comment_list = ""
    for i, c in enumerate(comments):
        comment_list += (
            f"\nComment {i+1} "
            f"[Subreddit: r/{c.get('subreddit','unknown')} | "
            f"Post: {c.get('post_title','')[:80]}]:\n"
            f"{c['content'][:600]}\n"
        )

    prompt = f"""
You are a senior strategy analyst briefing Disney's executive leadership.
Your ONLY job right now is to decide which comments contain genuine
operational or strategic intelligence that would change what a Disney VP
does on Monday morning.

You are extremely selective. Approve 1 in 20 comments at most.

THE CORE TEST:
"If I showed this to a Disney VP, would they know exactly what
operational or strategic action to take, and where?"
If the answer is anything other than an immediate yes — reject it.

HARD DISQUALIFIERS — reject instantly if any are true:

1. VIRAL STORY: Entertaining, relatable, funny, or emotionally resonant
   but not actionable. Bathroom stories, parenting fails, funny moments
   — stories, not intelligence.

2. GUEST BEHAVIOR PROBLEM: Root cause is other guests, not Disney's
   systems, staffing, or design.

3. BANNED RECOMMENDATION WORDS: If the only honest recommendation starts
   with Investigate, Enhance, Consider, Review, Look into, or Improve
   — reject. These mean the comment lacks specificity.

4. OBVIOUS: Disney already knows and tracks this. Long waits, crowds,
   expensive food — known. Reject unless the comment reveals a specific
   cause, location, time, or system failure Disney may not have isolated.

5. ONE-TIME INCIDENT: Single bad experience with no systemic signal.

6. NO CLEAR FIX: No operational solution Disney could implement.

WHAT QUALIFIES — all must be true:
- Names a specific system, location, attraction, or staff role
- Problem caused by Disney's design, staffing, or operations
- There is a concrete fix Disney could implement
- A Disney ops manager would know exactly what to go look at

Return ONLY a valid JSON array, one object per comment:
[
  {{
    "comment_number": 1,
    "is_insightful": true or false,
    "category": "operations|imagineering|maintenance|commercial|guest_services|risk",
    "sentiment": "positive|negative|neutral"
  }}
]

Comments to analyze:
{comment_list}

Return ONLY the JSON array. No preamble, no markdown, no explanation.
Expect to mark most comments is_insightful: false.
"""

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            text = response.choices[0].message.content.strip()
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            print(f"  Filter attempt {attempt+1} failed: {e}")
            if attempt < 2:
                time.sleep(2)
    return None


# ── PASS 2: Write-up ──────────────────────────────────────────────────────────

def writeup_batch(comments, high_tier=False):
    """Pass 2: Write up only the insightful comments.
    High tier (top 25% upvotes) gets full VP briefing detail.
    Standard tier gets concise bullet format."""

    comment_list = ""
    for i, c in enumerate(comments):
        comment_list += (
            f"\nComment {i+1} "
            f"[Subreddit: r/{c.get('subreddit','unknown')} | "
            f"Post: {c.get('post_title','')[:80]}]:\n"
            f"{c['content'][:600]}\n"
        )

    if high_tier:
        detail_instructions = """
OUTPUT FORMAT:

recommendation: A razor-sharp headline naming the exact fix, the exact
location, and the exact problem. Starts with a concrete action verb
(Deploy, Restore, Redesign, Restaff, Reprice, Add, Remove, Fix).
Never starts with Investigate, Enhance, Consider, Review, or Improve.

context_paragraph: 3-5 sentences that read like a VP briefing note.
Explain what is specifically happening, what the root cause appears to be,
what the guest impact is, and why this matters strategically. Reference
specific details from the comment. No filler. No generic observations.

supporting_quotes: 2-3 direct quotes under 15 words each that are
specific and striking — operational observations, not emotional reactions.

context_bullet: null
source_quote: null
"""
    else:
        detail_instructions = """
OUTPUT FORMAT:

recommendation: A razor-sharp headline naming the exact fix, the exact
location, and the exact problem. Starts with a concrete action verb.
Never starts with Investigate, Enhance, Consider, Review, or Improve.

context_bullet: One sentence naming the specific root cause or operational
detail that makes this finding actionable.

source_quote: The single most operationally specific quote from the
comment under 15 words.

context_paragraph: null
supporting_quotes: []
"""

    prompt = f"""
You are writing up pre-approved insightful comments for Disney's executive
leadership. These comments have already passed a quality filter — your job
is ONLY to write the recommendation and supporting detail.

Every comment you receive IS insightful. Write up all of them.

{detail_instructions}

Return ONLY a valid JSON array, one object per comment:
[
  {{
    "comment_number": 1,
    "recommendation": "concrete action verb headline",
    "context_paragraph": "VP briefing paragraph or null",
    "context_bullet": "one specific detail sentence or null",
    "source_quote": "most operationally specific quote under 15 words or null",
    "supporting_quotes": ["quote 1", "quote 2", "quote 3"]
  }}
]

Comments to write up:
{comment_list}

Return ONLY the JSON array. No preamble, no markdown, no explanation.
"""

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000
            )
            text = response.choices[0].message.content.strip()
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            print(f"  Writeup attempt {attempt+1} failed: {e}")
            if attempt < 2:
                time.sleep(2)
    return None


# ── Main processing loop ──────────────────────────────────────────────────────

def calculate_percentile(upvotes, all_upvotes):
    if not all_upvotes:
        return 50.0
    rank = sum(u <= upvotes for u in all_upvotes)
    return round((rank / len(all_upvotes)) * 100, 1)

def process_unscored_comments():
    print("\nPulling unprocessed comments...")

    all_comments = []
    page = 0
    page_size = 1000
    while True:
        result = supabase.table("raw_comments")\
            .select("*")\
            .eq("processed", False)\
            .range(page * page_size, (page + 1) * page_size - 1)\
            .execute()
        batch = result.data
        if not batch:
            break
        all_comments.extend(batch)
        page += 1
        print(f"  Fetched {len(all_comments)} so far...")
    comments = all_comments
    total = len(comments)
    print(f"Found {total} unprocessed comments\n")

    if not comments:
        print("Nothing to process.")
        return

    posts = {}
    for c in comments:
        pid = c.get('post_id', 'unknown')
        if pid not in posts:
            posts[pid] = []
        posts[pid].append(c)

    insights_found  = 0
    processed_count = 0
    batch_size      = 20

    for post_id, post_comments in posts.items():
        all_upvotes = [c.get('upvotes', 0) or 0 for c in post_comments]

        def get_percentile(upvotes):
            if not all_upvotes:
                return 50.0
            rank = sum(u <= upvotes for u in all_upvotes)
            return round((rank / len(all_upvotes)) * 100, 1)

        for i in range(0, len(post_comments), batch_size):
            batch = post_comments[i:i + batch_size]

            pct_done = round((processed_count / total) * 100, 1)
            print(f"\n[{pct_done}%] Post {post_id[:8]}... — {len(batch)} comments")

            # ── PASS 1: Filter for quality ────────────────────────────────
            filter_results = filter_batch(batch)

            if not filter_results:
                print("  Filter batch failed — skipping")
                for c in batch:
                    supabase.table("raw_comments").update({"processed": True}).eq("id", c['id']).execute()
                    processed_count += 1
                continue

            insightful_comments = []
            insightful_meta     = {}  # comment index → filter result

            for j, result in enumerate(filter_results):
                if j >= len(batch):
                    continue
                if result.get('is_insightful'):
                    insightful_comments.append(batch[j])
                    insightful_meta[len(insightful_comments) - 1] = result
                else:
                    # Mark non-insightful as processed immediately
                    try:
                        supabase.table("raw_comments")\
                            .update({"processed": True})\
                            .eq("id", batch[j]['id'])\
                            .execute()
                    except Exception as e:
                        print(f"  Error marking processed: {e}")
                    processed_count += 1
                    print(f"  discarded")

            if not insightful_comments:
                continue

            print(f"  {len(insightful_comments)} passed quality filter — writing up...")

            # ── PASS 2: Split by upvotes, write up detail ─────────────────
            high_batch     = [(idx, c) for idx, c in enumerate(insightful_comments)
                              if get_percentile(c.get('upvotes', 0) or 0) >= 75]
            standard_batch = [(idx, c) for idx, c in enumerate(insightful_comments)
                              if get_percentile(c.get('upvotes', 0) or 0) < 75]

            writeups = {}  # original index → writeup

            if high_batch:
                scores = writeup_batch([c for _, c in high_batch], high_tier=True)
                if scores:
                    for k, score in enumerate(scores):
                        if k < len(high_batch):
                            orig_idx = high_batch[k][0]
                            writeups[orig_idx] = (score, True)

            if standard_batch:
                scores = writeup_batch([c for _, c in standard_batch], high_tier=False)
                if scores:
                    for k, score in enumerate(scores):
                        if k < len(standard_batch):
                            orig_idx = standard_batch[k][0]
                            writeups[orig_idx] = (score, False)

            # ── Save insights ─────────────────────────────────────────────
            for idx, comment in enumerate(insightful_comments):
                if idx not in writeups:
                    # Writeup failed for this comment — still mark processed
                    try:
                        supabase.table("raw_comments")\
                            .update({"processed": True})\
                            .eq("id", comment['id'])\
                            .execute()
                    except Exception as e:
                        print(f"  Error marking processed: {e}")
                    processed_count += 1
                    continue

                score, is_high = writeups[idx]
                filter_meta    = insightful_meta[idx]

                subreddit    = comment.get('subreddit', '')
                post_title   = comment.get('post_title', '')
                content      = comment.get('content', '')
                experience   = infer_experience(subreddit, content, post_title)
                project_tags = assign_project_tags(content, post_title)
                percentile   = get_percentile(comment.get('upvotes', 0) or 0)
                featured     = percentile >= 75
                weighted     = max(comment.get('upvotes', 0) or 0, 1)
                tier_label   = "HIGH" if is_high else "STD"

                print(f"  ✓ [{tier_label}] {filter_meta['category']} | {score.get('recommendation','')[:80]}...")

                try:
                    supabase.table("insights").insert({
                        "raw_comment_id":        comment['id'],
                        "experience_tag":        experience,
                        "category_tag":          filter_meta['category'],
                        "recommendation":        score.get('recommendation'),
                        "context_paragraph":     score.get('context_paragraph'),
                        "context_bullet":        score.get('context_bullet'),
                        "source_quote":          score.get('source_quote'),
                        "supporting_quotes":     score.get('supporting_quotes', []),
                        "insight_quality_score": 10.0,
                        "upvotes":               comment.get('upvotes', 0),
                        "upvote_percentile":     percentile,
                        "featured":              featured,
                        "weighted_score":        weighted,
                        "sentiment":             filter_meta.get('sentiment', 'neutral'),
                        "project_tags":          project_tags,
                        "username":              comment.get('username'),
                        "date_posted":           comment.get('date_posted'),
                        "comment_url":           comment.get('comment_url'),
                        "week_number":           1
                    }).execute()
                    insights_found += 1
                except Exception as e:
                    print(f"  Error saving insight: {e}")

                try:
                    supabase.table("raw_comments")\
                        .update({"processed": True})\
                        .eq("id", comment['id'])\
                        .execute()
                except Exception as e:
                    print(f"  Error marking processed: {e}")

                processed_count += 1

    print(f"\n{'='*50}")
    print(f"Done. {insights_found} gems from {processed_count} comments")
    if processed_count > 0:
        print(f"Signal rate: {round(insights_found/processed_count*100,1)}%")

import time

while True:
    process_unscored_comments()
    result = supabase.table("raw_comments").select("id", count="exact").eq("processed", False).execute()
    remaining = result.count or 0
    if remaining == 0:
        print("All comments processed!")
        break
    print(f"\n{remaining} still unprocessed — retrying in 10 seconds...")
    time.sleep(10)
