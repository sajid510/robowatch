"""Offline sample data so the pipeline can be demoed and tested without
network access or API keys (``--offline`` flag in ``src.main``).

Every item mirrors the shape produced by :mod:`src.fetchers` so the rest of
the pipeline (enrichment, fallback builder, mailer) works unchanged.
"""

from datetime import datetime, timedelta, timezone

SAMPLE_ITEMS = [
    {
        "title": "Learning Robust Autonomous Navigation with SLAM in ROS 2",
        "url": "https://arxiv.org/abs/2506.00001",
        "source": "arXiv cs.RO",
        "published_date": datetime.now(timezone.utc) - timedelta(days=1),
        "raw_text": "A framework for robust indoor navigation on low-cost robots "
                     "combining LiDAR SLAM, path planning and sensor fusion.",
        "category": "research",
    },
    {
        "title": "Edge-Cloud Compute Partitioning for Mobile Robot Perception",
        "url": "https://arxiv.org/abs/2506.00002",
        "source": "arXiv cs.CV",
        "published_date": datetime.now(timezone.utc) - timedelta(days=2),
        "raw_text": "Presents a two-layer architecture that splits perception "
                     "between an on-robot edge device and a remote compute node.",
        "category": "research",
    },
    {
        "title": "Open-Source ROS 2 Nav2 Tutorial Series for Student Teams",
        "url": "https://www.therobotreport.com/nav2-tutorial-series",
        "source": "The Robot Report",
        "published_date": datetime.now(timezone.utc) - timedelta(days=3),
        "raw_text": "Hands-on guide walking student teams through mapping, "
                     "localization and path planning with Nav2 on a budget robot.",
        "category": "industry",
    },
    {
        "title": "New Low-Cost LiDAR Sensors Reshape Indoor Robot Navigation",
        "url": "https://spectrum.ieee.org/low-cost-lidar-2026",
        "source": "IEEE Spectrum",
        "published_date": datetime.now(timezone.utc) - timedelta(days=4),
        "raw_text": "A new generation of low-cost 2D LiDAR sensors makes SLAM "
                     "feasible for undergraduate and hobbyist robot builds.",
        "category": "industry",
    },
    {
        "title": "International Undergraduate Robotics Challenge — Registration Open",
        "url": "https://devpost.com/hackathons/undergrad-robotics-2026",
        "source": "Devpost",
        "published_date": datetime.now(timezone.utc) - timedelta(days=5),
        "raw_text": "Open to international student teams. Hardware + autonomous "
                     "navigation track. Prizes and travel grants available.",
        "category": "competition",
    },
    {
        "title": "IEEE Robotics Fellowship for Students in Developing Countries",
        "url": "https://www.ieee.org/fellowship-2026",
        "source": "IEEE",
        "published_date": datetime.now(timezone.utc) - timedelta(days=6),
        "raw_text": "Fellowship supporting undergraduate students in developing "
                     "countries working on robotics research projects.",
        "category": "fellowship",
    },
    {
        "title": "Dhaka University Robotics Fest 2026 — Line Follower and SLAM Maze",
        "url": "https://news.google.com/rss/search?q=robotics+Bangladesh",
        "source": "Google News BD",
        "published_date": datetime.now(timezone.utc) - timedelta(days=2),
        "raw_text": "National robotics festival with autonomous maze-solving and "
                     "line-follower categories open to all universities.",
        "category": "bangladesh",
    },
    {
        "title": "ICRA 2027 Call for Papers — Deadline Announced",
        "url": "https://www.google.com/search?q=ICRA+2027+call+for+papers",
        "source": "CFP Tracker",
        "published_date": datetime.now(timezone.utc),
        "raw_text": "Conference: IEEE International Conference on Robotics and "
                     "Automation. Venue: TBD. Known submission deadline: "
                     "~October 2026 (estimated abstract deadline).",
        "category": "cfp",
        "cfp_name": "ICRA 2027",
        "cfp_venue": "TBD",
        "cfp_known_deadline": "~October 2026 (estimated)",
    },
    {
        "title": "IEEE RAAICON 2026 — Call for Papers (Dhaka, Bangladesh)",
        "url": "https://www.google.com/search?q=IEEE+RAAICON+2026",
        "source": "CFP Tracker",
        "published_date": datetime.now(timezone.utc),
        "raw_text": "Conference: IEEE Recent Advances in AI and IOT for Converged "
                     "Networks. Venue: Dhaka, Bangladesh. Near-zero travel cost.",
        "category": "cfp",
        "cfp_name": "IEEE RAAICON 2026",
        "cfp_venue": "Dhaka, Bangladesh",
        "cfp_known_deadline": None,
    },
]


def sample_items():
    """Return a copy of the offline sample items."""
    import copy
    return copy.deepcopy(SAMPLE_ITEMS)
