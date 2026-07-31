# Architecture 06 — Security

## Threat model

The system runs on GitHub Actions, talks to three external APIs, and sends
email. Key risks: secret leakage, prompt injection from feed content, and
injection into generated HTML.

## Controls

### Secrets

- Keys are **only** read from environment variables / GitHub secrets.
- `docker-compose.yml` references `.env`; `.env` and `output/` are git-ignored.
- Gmail uses an **app password** (scoped, revocable) over SMTP/SSL 465 — never
  the account password.

### Prompt injection

Feed titles/summaries are untrusted text passed to LLMs. Mitigations:
- System prompts strictly constrain output ("Respond ONLY with valid JSON… No
  explanation. No markdown.").
- Numeric/boolean fields are coerced and clamped (`int`, `bool`, priority
  whitelist) after parsing.
- Deadlines are normalized to `YYYY-MM-DD` via `datetime.fromisoformat`.

### HTML injection into the report

- Item URLs and text are rendered into email HTML. The fallback builder
  `escHtml`-style sanitation is used for untrusted fields (titles, summaries).
- Gemini-generated HTML is the accepted output of the narrator and is treated
  as trusted within the email scope.

### Subscriber list

- `subscribers.txt` is committed — email addresses are semi-public by design
  for this project. Unsubscribe = remove the line and push.

### Supply chain

- `requirements.txt` pins package versions.
- Docker uses a pinned base image (`python:3.11-slim`).

## Reporting

See [`SECURITY.md`](../SECURITY.md): report vulnerabilities privately to the
maintainer before public disclosure.
