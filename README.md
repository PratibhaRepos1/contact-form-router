# Contact Form Router

AI-powered contact form that classifies incoming messages by intent
(`sales` | `support` | `partnership` | `spam`) using the Anthropic Claude API
and forwards them to the matching Slack channel.

**Live demo:** https://contact-form-router-sandy.vercel.app

## How it works

1. **You write** — fill in name, email, and message.
2. **Claude reads** — the backend sends the message to the Anthropic API with a structured system prompt; Claude returns a JSON object with category, confidence, and a one-sentence reasoning.
3. **Slack receives** — the backend posts the submission to the matching team webhook (`#sales`, `#support`, `#partnerships`, or `#spam-archive`).
4. **You see why** — the UI shows the category, confidence, reasoning, and which channel it was routed to.

## Stack

- **Frontend:** React 18 + Vite + Tailwind CSS
- **Backend:** Python 3.11+ · FastAPI · Uvicorn
- **AI:** Anthropic Claude (`claude-sonnet-4-20250514`)
- **Integrations:** Slack Incoming Webhooks
- **Hosting:** Vercel (frontend as static site, backend as Python serverless function)
- **CI:** GitHub Actions (build + import smoke test on every push)

## Setup

### 1. Backend

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # then fill in your keys
uvicorn main:app --reload --port 8000
```

Required env vars (see `backend/.env.example`):

- `ANTHROPIC_API_KEY`
- `SLACK_SALES_WEBHOOK`
- `SLACK_SUPPORT_WEBHOOK`
- `SLACK_PARTNERSHIP_WEBHOOK`
- `SLACK_SPAM_WEBHOOK`
- `CORS_ORIGINS` (optional, comma-separated; defaults to `http://localhost:5173`)

If a Slack webhook is missing, the API still returns a classification — the
response just shows `slack_posted: false`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
# http://localhost:5173
```

Vite proxies `/api/*` → `http://localhost:8000`, so no CORS hassle in dev.

## API

`POST /api/classify`

```json
{
  "name": "John Smith",
  "email": "john@example.com",
  "message": "I'd like to discuss a partnership opportunity"
}
```

Response:

```json
{
  "category": "partnership",
  "confidence": "high",
  "reasoning": "Message explicitly mentions partnership opportunity",
  "slack_posted": true,
  "routed_to": "#partnerships"
}
```

`GET /api/health` → `{"status": "ok"}`

## Deployment (Vercel)

The repo is set up as **two separate Vercel projects** sharing the same GitHub repo:

| Project       | Root Directory | Purpose                                    |
|---------------|----------------|--------------------------------------------|
| Frontend      | `frontend`     | Static Vite build, rewrites `/api/*` → backend |
| Backend       | `backend`      | FastAPI on `@vercel/python` runtime        |

**Frontend** (`frontend/vercel.json`) detects Vite automatically and rewrites
`/api/:path*` to the backend's production URL so the browser sees a same-origin
API.

**Backend** (`backend/vercel.json`) uses the `@vercel/python` builder to run
`main.py` as a serverless function and routes every request to it.

Vercel's GitHub integration auto-deploys on every push to `main`. Add the
required env vars in each project's **Settings → Environment Variables**
before the first deploy.

## CI

`.github/workflows/ci.yml` runs on every push and pull request to `main`:

- **build-frontend** — `npm ci` + `npm run build`, uploads `dist/` as artifact.
- **build-backend** — installs `requirements.txt`, byte-compiles all sources, and runs an import smoke test on the FastAPI app.

Vercel handles the actual deploys; CI is purely for build verification.

## Project layout

```
contact-form-router/
├── frontend/                # React + Vite + Tailwind
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── ContactForm.jsx
│   │   │   └── ResultPanel.jsx
│   │   └── ...
│   └── vercel.json          # Vite config + /api rewrite to backend
├── backend/                 # FastAPI + Anthropic + Slack
│   ├── main.py              # FastAPI app, CORS, routes
│   ├── classifier.py        # Anthropic API call
│   ├── slack.py             # Slack webhook sender
│   ├── models.py            # Pydantic request/response models
│   ├── requirements.txt
│   └── vercel.json          # @vercel/python config
├── .github/workflows/ci.yml # Build + validation
├── CLAUDE.md                # Full project spec
└── README.md
```

## Portfolio context

Project #1 of 13 AI-powered applications built for a career transition portfolio
from Senior Frontend Developer to AI Developer.

Developer: Pratibha · Stack: React, Angular, 16 years IT, 2+ years Gen AI
Portfolio: https://pratibharepos1.github.io/crafted-by-pratibha/
