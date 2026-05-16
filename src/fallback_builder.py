# Used when Gemini narrative generation fails.
# Produces a clean structured HTML report from enriched items.

def build_fallback_report(items):
    sections = [
        ("🏭 Industry & Breakthroughs", ["industry"]),
        ("📄 Research Spotlight",       ["research"]),
        ("🏆 Competitions & Opportunities", ["competition", "conference", "fellowship"]),
        ("🇧🇩 Bangladesh Robotics Scene",   ["bangladesh"]),
    ]

    def card(item):
        p = item.get("priority", "MEDIUM")
        score = item.get("score", 5)
        deadline_html = ""
        if item.get("deadline"):
            deadline_html = f'<span class="deadline"> | ⏰ Deadline: {item["deadline"]}</span>'
        bd_html = " | 🇧🇩 BD Eligible" if item.get("bd_relevant") else ""
        tech_html = ""
        if item.get("key_tech"):
            tech_html = " | 🔧 " + ", ".join(item["key_tech"])

        return f"""
<div class="card {p}">
  <div class="card-header">
    <span class="badge badge-{p}">{p}</span>
    <span class="score">Score: {score}/10</span>
  </div>
  <h3><a href="{item['url']}">{item['title']}</a></h3>
  <p class="summary">{item.get('summary', '')}</p>
  <p class="reasoning"><em>Why this matters: {item.get('reasoning', '')}</em></p>
  <div class="meta">📰 {item['source']} | 📅 {item['published_date'].strftime('%b %d, %Y')}{deadline_html}{bd_html}{tech_html}</div>
</div>"""

    html_parts = []

    # High priority alert box
    high_items = [i for i in items if i.get("priority") == "HIGH"]
    if high_items:
        html_parts.append('<div class="editor-brief"><p><strong>⚡ This week\'s highlights:</strong> '
                         f'{len(high_items)} high-priority items require your attention. '
                         'Check the Team Action section for specific next steps.</p></div>')

    for section_title, categories in sections:
        section_items = [i for i in items if i.get("category") in categories]
        if not section_items:
            continue
        html_parts.append(f"<h2>{section_title}</h2>")
        for item in section_items:
            html_parts.append(card(item))

    # Action checklist from HIGH items
    if high_items:
        html_parts.append('<h2>✅ Team Action Checklist</h2>')
        html_parts.append('<div class="checklist"><ul>')
        for item in high_items[:6]:
            action = f'Review: <a href="{item["url"]}">{item["title"][:70]}</a>'
            if item.get("deadline"):
                action = f'⏰ Before {item["deadline"]} — {action}'
            html_parts.append(f"<li>{action}</li>")
        html_parts.append("</ul></div>")

    # Quick scan (LOW)
    low_items = [i for i in items if i.get("priority") == "LOW"]
    if low_items:
        html_parts.append("<h2>🔍 Quick Scan</h2>")
        for item in low_items[:10]:
            html_parts.append(
                f'<p style="font-size:13px;color:#888;">• '
                f'<a href="{item["url"]}">{item["title"]}</a> '
                f'— {item["source"]}</p>'
            )

    return "\n".join(html_parts)
