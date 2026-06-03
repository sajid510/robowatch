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

    # CFP Paper Submission Tracker section
    cfp_items = [i for i in items if i.get("category") == "cfp"]
    if cfp_items:
        html_parts.append("<h2>📝 Paper Submission Tracker</h2>")
        html_parts.append(
            '<div class="editor-brief"><p>'
            f'Tracking <strong>{len(cfp_items)} target conferences</strong> '
            'for your autonomous robot paper. Sorted by fit score.'
            '</p></div>'
        )
        for item in cfp_items:
            p = item.get("priority", "MEDIUM")
            score = item.get("score", 7)
            deadline_row = item.get("deadline") or item.get("cfp_known_deadline") or "TBA"
            conf_date = item.get("cfp_conference_date", "TBA")
            location = item.get("cfp_location", item.get("cfp_venue", "TBD"))
            sub_type = item.get("cfp_submission_type", "Unknown")
            fee = item.get("cfp_fee", "Unknown — check official site")
            action = item.get("cfp_action", "Monitor official site")
            html_parts.append(f"""
<div class="card cfp-card {p}">
  <div class="card-header">
    <span class="badge badge-{p}">FIT: {score}/10</span>
    <span class="score">📝 CFP</span>
  </div>
  <h3><a href="{item['url']}">{item.get('cfp_name', item['title'])}</a></h3>
  <p class="summary">{item.get('summary', '')}</p>
  <table class="cfp-table">
    <tr><td>📅 Submission Deadline</td><td><strong>{deadline_row}</strong></td></tr>
    <tr><td>🗓️ Conference Date</td><td>{conf_date}</td></tr>
    <tr><td>📍 Venue</td><td>{location}</td></tr>
    <tr><td>📄 Submission Type</td><td>{sub_type}</td></tr>
    <tr><td>💰 Fee</td><td>{fee}</td></tr>
  </table>
  <div class="cfp-action">⚡ Action: {action}</div>
  <p class="reasoning"><em>Why it fits: {item.get('reasoning', '')}</em></p>
</div>""")
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
