import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from datetime import date

EMAIL_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
  body { font-family: 'Inter', Arial, sans-serif; background: #0a0a14;
         color: #e0e0e0; margin: 0; padding: 16px; }
  .wrapper { max-width: 780px; margin: 0 auto; }
  .header { background: linear-gradient(135deg, #e94560 0%, #0f3460 100%);
             color: white; padding: 24px 28px; border-radius: 12px 12px 0 0;
             margin-bottom: 0; }
  .header h1 { margin: 0; font-size: 22px; font-weight: 700; }
  .header p { margin: 6px 0 0 0; opacity: 0.8; font-size: 13px; }
  .content { background: #12122a; padding: 24px 28px;
             border-radius: 0 0 12px 12px; }
  h2 { color: #e94560; border-bottom: 2px solid #1e1e3f;
       padding-bottom: 8px; margin: 32px 0 16px 0;
       font-size: 15px; text-transform: uppercase; letter-spacing: 1.5px; }
  .card { background: #1a1a35; border-left: 4px solid #333;
          padding: 16px 18px; margin: 12px 0; border-radius: 8px;
          transition: border-color 0.2s; }
  .card.HIGH { border-color: #e94560; }
  .card.MEDIUM { border-color: #f5a623; }
  .card.LOW { border-color: #4a9aba; }
  .card-header { display: flex; justify-content: space-between;
                 align-items: center; margin-bottom: 10px; }
  .badge { padding: 3px 12px; border-radius: 20px; font-size: 11px;
           font-weight: 700; letter-spacing: 0.5px; color: white; }
  .badge-HIGH { background: #e94560; }
  .badge-MEDIUM { background: #f5a623; color: #1a1a2e; }
  .badge-LOW { background: #4a9aba; }
  .score { font-size: 12px; color: #666; font-weight: 600; }
  h3 { margin: 6px 0 8px 0; font-size: 15px; line-height: 1.4; }
  h3 a { color: #7ec8e3; text-decoration: none; }
  h3 a:hover { text-decoration: underline; color: #e94560; }
  .summary { color: #ccc; font-size: 14px; line-height: 1.65;
             margin: 8px 0; }
  .reasoning { color: #777; font-size: 13px; margin: 6px 0;
               font-style: italic; }
  .meta { font-size: 12px; color: #555; margin-top: 10px;
          padding-top: 8px; border-top: 1px solid #1e1e3f; }
  .deadline { color: #e94560; font-weight: 600; }
  .editor-brief { background: #0f1f40; border-radius: 10px;
                  padding: 18px 22px; margin: 16px 0;
                  border-left: 5px solid #e94560; }
  .editor-brief p { margin: 0; line-height: 1.7; color: #ddd; }
  .top-pick { background: #1a0810; border: 2px solid #e94560;
              border-radius: 10px; padding: 18px 22px; margin: 16px 0; }
  .top-pick p { color: #ddd; line-height: 1.7; }
  .checklist { background: #0a1628; border-radius: 10px;
               padding: 18px 22px; margin: 16px 0; }
  .checklist ul { margin: 0; padding-left: 20px; }
  .checklist li { margin: 10px 0; color: #ccc; line-height: 1.6; }
  .checklist li::marker { color: #e94560; }
  .footer { text-align: center; color: #333; font-size: 11px;
            margin-top: 24px; padding-top: 16px;
            border-top: 1px solid #1e1e3f; line-height: 1.8; }
  a { color: #7ec8e3; }
</style>
"""

EMAIL_WRAPPER = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RoboWatch Weekly Report</title>
  {css}
</head>
<body>
  <div class="wrapper">
    <div class="header">
      <h1>🤖 RoboWatch Weekly Intelligence</h1>
      <p>Week of {date} &nbsp;·&nbsp; AI-Powered Robotics Digest &nbsp;·&nbsp; {count} items tracked</p>
    </div>
    <div class="content">
      {body}
    </div>
    <div class="footer">
      RoboWatch &nbsp;·&nbsp; Groq llama-3.3-70b + Gemini 2.5 Flash &nbsp;·&nbsp; GitHub Actions<br>
      Built by Niyari · University of Asia Pacific, Bangladesh<br>
      To unsubscribe: remove your email from subscribers.txt and push to GitHub
    </div>
  </div>
</body>
</html>"""


def load_subscribers():
    """Load email list from subscribers.txt."""
    path = Path("subscribers.txt")
    if not path.exists():
        print("  [WARN] subscribers.txt not found!")
        return []

    emails = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and "@" in line and not line.startswith("#"):
            emails.append(line)

    return emails


def send_report(html_body, item_count=0):
    """Send the report to all subscribers via Gmail SMTP."""
    sender = os.environ.get("GMAIL_ADDRESS", "")
    password = os.environ.get("GMAIL_APP_PASSWORD", "")

    if not sender or not password:
        print("  [ERROR] Gmail credentials not set in environment variables")
        return False

    subscribers = load_subscribers()
    if not subscribers:
        print("  [ERROR] No subscribers found in subscribers.txt")
        return False

    # Build full HTML email
    full_html = EMAIL_WRAPPER.format(
        css=EMAIL_CSS,
        date=date.today().strftime("%B %d, %Y"),
        body=html_body,
        count=item_count
    )

    subject = (
        f"🤖 RoboWatch — Robotics Intelligence | "
        f"Week of {date.today().strftime('%b %d, %Y')}"
    )

    print(f"  Connecting to Gmail SMTP...")
    success_count = 0

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            print(f"  Logged in. Sending to {len(subscribers)} subscriber(s)...")

            for recipient in subscribers:
                try:
                    msg = MIMEMultipart("alternative")
                    msg["Subject"] = subject
                    msg["From"] = f"RoboWatch <{sender}>"
                    msg["To"] = recipient
                    msg["Reply-To"] = sender
                    msg.attach(MIMEText(full_html, "html", "utf-8"))

                    server.sendmail(sender, [recipient], msg.as_string())
                    print(f"  ✓ Delivered → {recipient}")
                    success_count += 1

                except Exception as e:
                    print(f"  ✗ Failed → {recipient}: {e}")

    except smtplib.SMTPAuthenticationError:
        print("  [ERROR] Gmail authentication failed. Check GMAIL_APP_PASSWORD.")
        return False
    except Exception as e:
        print(f"  [ERROR] SMTP connection failed: {e}")
        return False

    print(f"  Delivery complete: {success_count}/{len(subscribers)} sent")
    return success_count > 0
