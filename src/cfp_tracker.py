"""
cfp_tracker.py
Dedicated module for paper submission / Call For Papers intelligence.
Tracks target conferences for Team Supersonic's autonomous robot project.
"""

import feedparser
from datetime import datetime, timezone

# ── PROJECT CONTEXT ───────────────────────────────────────────────────────────
# Used by the enricher to score CFP fit against your specific project.
PROJECT_KEYWORDS = [
    "ROS 2", "ROS2", "Jetson Nano", "SLAM", "Nav2", "LiDAR", "RPLidar",
    "Kinect", "depth camera", "IMU", "MPU6050", "Arduino",
    "autonomous navigation", "indoor navigation", "mobile robot",
    "sensor fusion", "edge computing", "GPS-denied", "occupancy map",
    "path planning", "obstacle avoidance", "localization", "mapping",
    "Zenoh", "DDS", "VPN", "distributed robotics", "Docker",
    "edge cloud", "compute partitioning", "pub sub middleware",
    "autonomous mobile robot", "AMR", "service robot", "ground robot",
]

# ── TARGET CONFERENCES ────────────────────────────────────────────────────────
TARGET_CONFERENCES = [
    {
        "name": "ICCIR 2026",
        "full_name": "International Conference on Computing and Intelligent Robotics",
        "search_query": "ICCIR 2026 robotics paper submission",
        "known_venue": "TBD",
        "known_deadline": None,
        "notes": "Covers intelligent robotics and autonomous systems — direct scope match.",
        "relevance": "HIGH",
        "bd_relevant": False,
    },
    {
        "name": "ROSCon 2026",
        "full_name": "ROSCon — Official ROS Community Conference",
        "search_query": "ROSCon 2026 talk proposal submission",
        "known_venue": "TBD (rotates annually)",
        "known_deadline": None,
        "notes": "Perfect fit — ROS2, Zenoh middleware, Nav2, and Docker-on-Jetson are core ROSCon topics.",
        "relevance": "HIGH",
        "bd_relevant": False,
    },
    {
        "name": "IEEE RAAICON 2026",
        "full_name": "IEEE Recent Advances in AI and IOT for Converged Networks",
        "search_query": "IEEE RAAICON 2026 Bangladesh call for papers",
        "known_venue": "Dhaka, Bangladesh",
        "known_deadline": None,
        "notes": "BD-based IEEE venue. Edge AI + autonomous robotics fits squarely. Near-zero travel cost.",
        "relevance": "HIGH",
        "bd_relevant": True,
    },
    {
        "name": "ICRA/IROS Workshop 2026",
        "full_name": "IEEE ICRA / IROS Workshops",
        "search_query": "ICRA 2026 workshop call for papers autonomous navigation",
        "known_venue": "ICRA 2026: Atlanta USA | IROS 2026: TBD",
        "known_deadline": None,
        "notes": "Workshops are easier first-publication targets than main track. Indoor navigation and ROS2 workshops appear every year.",
        "relevance": "HIGH",
        "bd_relevant": False,
    },
    {
        "name": "ICRA 2027",
        "full_name": "IEEE International Conference on Robotics and Automation",
        "search_query": "ICRA 2027 call for papers submission deadline",
        "known_venue": "TBD",
        "known_deadline": "~October 2026 (estimated abstract deadline)",
        "notes": "Top-tier robotics venue. Abstract deadline ~15 months before conference. Start drafting by mid-2026.",
        "relevance": "HIGH",
        "bd_relevant": False,
    },
    {
        "name": "ROBIO 2026",
        "full_name": "IEEE International Conference on Robotics and Biomimetics",
        "search_query": "ROBIO 2026 IEEE call for papers",
        "known_venue": "Asia-Pacific (rotates annually)",
        "known_deadline": None,
        "notes": "Good fit for mobile robot navigation and sensor fusion. Typically held December, submission ~July-August.",
        "relevance": "HIGH",
        "bd_relevant": False,
    },
    {
        "name": "IROS 2026",
        "full_name": "IEEE/RSJ International Conference on Intelligent Robots and Systems",
        "search_query": "IROS 2026 call for papers submission deadline",
        "known_venue": "TBD",
        "known_deadline": "~March 2026 (estimated)",
        "notes": "Second-largest robotics conference after ICRA. Strong fit for autonomous navigation and SLAM.",
        "relevance": "HIGH",
        "bd_relevant": False,
    },
    {
        "name": "ECMR 2026",
        "full_name": "European Conference on Mobile Robots",
        "search_query": "ECMR 2026 call for papers mobile robot",
        "known_venue": "Europe",
        "known_deadline": None,
        "notes": "Specialized in mobile robot navigation — directly relevant to your project scope.",
        "relevance": "MEDIUM",
        "bd_relevant": False,
    },
    {
        "name": "IEEE IRC 2026",
        "full_name": "IEEE International Conference on Robotic Computing",
        "search_query": "IEEE IRC 2026 robotic computing paper",
        "known_venue": "TBD",
        "known_deadline": None,
        "notes": "Covers edge computing + robotics intersection — matches your Jetson Nano edge layer directly.",
        "relevance": "MEDIUM",
        "bd_relevant": False,
    },
    {
        "name": "ICARCV 2026",
        "full_name": "International Conference on Control, Automation, Robotics and Vision",
        "search_query": "ICARCV 2026 call for papers",
        "known_venue": "Asia-Pacific",
        "known_deadline": None,
        "notes": "Strong Asia-Pacific presence. Covers control + autonomous navigation. Accessible for BD teams.",
        "relevance": "MEDIUM",
        "bd_relevant": False,
    },
    {
        "name": "IEEE Bangladesh Section Conferences",
        "full_name": "IEEE ECCE / TENSYMP / STI — Bangladesh & Regional",
        "search_query": "IEEE Bangladesh conference robotics 2026 call for papers",
        "known_venue": "Bangladesh / South Asia",
        "known_deadline": None,
        "notes": "Regional IEEE venues with low travel cost. Good first-publication target for BD student teams.",
        "relevance": "MEDIUM",
        "bd_relevant": True,
    },
]


def _fetch_latest_news(conf):
    """Fetch most recent Google News entry for this conference."""
    query = conf["search_query"].replace(" ", "+")
    url = (
        f"https://news.google.com/rss/search?q={query}"
        f"&hl=en-US&gl=US&ceid=US:en"
    )
    try:
        feed = feedparser.parse(url)
        if feed.entries:
            return feed.entries[0]
    except Exception:
        pass
    return None


def _build_search_url(conf):
    q = conf["name"].replace(" ", "+")
    return f"https://www.google.com/search?q={q}+call+for+papers"


def fetch_all_cfp_targets():
    """
    Check all target conferences and return a list of structured items
    compatible with the existing enrichment + report pipeline.
    """
    print(f"    Checking {len(TARGET_CONFERENCES)} target conferences...")
    items = []

    for conf in TARGET_CONFERENCES:
        print(f"      → {conf['name']}...")
        latest = _fetch_latest_news(conf)

        # Build raw_text from all known info + any live news
        news_snippet = ""
        news_url = _build_search_url(conf)
        if latest:
            import re
            snippet = re.sub(r"<[^>]+>", " ", latest.get("summary", ""))
            snippet = re.sub(r"\s+", " ", snippet).strip()
            news_snippet = f" Latest news: {latest.get('title', '')}. {snippet[:300]}"
            news_url = latest.get("link", news_url)

        raw_text = (
            f"Conference: {conf['full_name']}. "
            f"Venue: {conf['known_venue']}. "
            f"Known submission deadline: {conf['known_deadline'] or 'Not yet announced'}. "
            f"Relevance to project: {conf['notes']}"
            f"{news_snippet}"
        )

        item = {
            # Standard pipeline fields
            "title": f"{conf['name']} — {conf['full_name']}",
            "url": news_url,
            "source": f"CFP Tracker",
            "published_date": datetime.now(timezone.utc),
            "raw_text": raw_text,
            "category": "cfp",
            # CFP-specific metadata (used by enricher + report)
            "cfp_name": conf["name"],
            "cfp_venue": conf["known_venue"],
            "cfp_known_deadline": conf["known_deadline"],
            "cfp_notes": conf["notes"],
            "cfp_has_news": latest is not None,
            # Pre-set scores so fallback still works if enricher skips
            "score": 10 if conf["relevance"] == "HIGH" else 7,
            "priority": conf["relevance"],
            "summary": (
                f"{conf['full_name']}. "
                f"Venue: {conf['known_venue']}. "
                f"Deadline: {conf['known_deadline'] or 'TBA — monitor official site'}. "
                f"{conf['notes']}"
            ),
            "reasoning": conf["notes"],
            "deadline": conf["known_deadline"],
            "bd_relevant": conf["bd_relevant"],
            "key_tech": ["ROS2", "SLAM", "autonomous navigation", "sensor fusion"],
        }
        items.append(item)

    print(f"    CFP targets loaded: {len(items)} conferences")
    return items
