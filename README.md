# Contact Form Router

AI-powered contact form that classifies incoming messages by intent
(`sales` | `support` | `partnership` | `spam`) using the Anthropic Claude API
and forwards them to the matching Slack channel.

## Stack

- **Frontend:** React 18 + Vite + Tailwind CSS
- **Backend:** Python 3.11+ · FastAPI · Uvicorn
- **AI:** Anthropic Claude (`claude-sonnet-4-20250514`)
- **Integrations:** Slack Incoming Webhooks

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

## Project layout

```
contact-form-router/
├── frontend/   # React + Vite + Tailwind
├── backend/    # FastAPI + Anthropic + Slack
├── CLAUDE.md   # Full project spec
└── README.md
```
