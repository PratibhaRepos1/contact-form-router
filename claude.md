# Contact Form Router — Claude Code Context

## Project Overview

An AI-powered contact form that classifies incoming messages by intent and routes
them to the correct Slack channel automatically. Built as a portfolio project to
demonstrate applied AI development with a React frontend and Python backend.

**Live demo flow:**
1. User fills contact form (name, email, message)
2. React sends data to FastAPI backend
3. Backend calls Anthropic Claude API to classify intent
4. Claude returns: `sales` | `support` | `partnership` | `spam`
5. Backend posts to matching Slack webhook
6. React UI displays classification result with confidence and routing info

---

## Tech Stack

| Layer        | Technology                          |
|--------------|-------------------------------------|
| Frontend     | React 18 + Vite + Tailwind CSS      |
| Backend      | Python 3.11+ · FastAPI · Uvicorn    |
| AI           | Anthropic Claude API (claude-sonnet-4-20250514) |
| Integrations | Slack Incoming Webhooks             |
| HTTP Client  | Axios (frontend) · requests (backend) |
| Env vars     | python-dotenv                       |

---

## Folder Structure

```
contact-form-router/
├── frontend/
│   ├── src/
│   │   ├── App.jsx                  # Root component, holds state
│   │   ├── components/
│   │   │   ├── ContactForm.jsx      # Form UI (name, email, message)
│   │   │   └── ResultPanel.jsx      # Shows classification result
│   │   ├── main.jsx                 # Entry point
│   │   └── index.css                # Tailwind imports
│   ├── index.html
│   ├── package.json
│   └── vite.config.js               # Proxy /api → localhost:8000
├── backend/
│   ├── main.py                      # FastAPI app, CORS, routes
│   ├── classifier.py                # Anthropic API call + classification logic
│   ├── slack.py                     # Slack webhook sender
│   ├── models.py                    # Pydantic request/response models
│   ├── requirements.txt
│   └── .env                         # API keys (never commit this)
├── CLAUDE.md                        # This file
└── README.md
```

---

## Environment Variables

File: `backend/.env`

```
ANTHROPIC_API_KEY=your_anthropic_key_here
SLACK_SALES_WEBHOOK=https://hooks.slack.com/services/xxx/yyy/zzz
SLACK_SUPPORT_WEBHOOK=https://hooks.slack.com/services/xxx/yyy/zzz
SLACK_PARTNERSHIP_WEBHOOK=https://hooks.slack.com/services/xxx/yyy/zzz
SLACK_SPAM_WEBHOOK=https://hooks.slack.com/services/xxx/yyy/zzz
```

**Never hardcode API keys. Always load from .env using python-dotenv.**

---

## Backend — Key Implementation Details

### API Endpoint

```
POST /api/classify
Content-Type: application/json

Request body:
{
  "name": "John Smith",
  "email": "john@example.com",
  "message": "I'd like to discuss a potential partnership opportunity"
}

Response:
{
  "category": "partnership",
  "confidence": "high",
  "reasoning": "Message explicitly mentions partnership opportunity",
  "slack_posted": true,
  "routed_to": "#partnerships"
}
```

### Classification Logic (classifier.py)

Use the Anthropic API with a structured system prompt. Claude must return JSON only.

```python
import anthropic
import json
import os

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a contact form classifier for a business website.

Classify the incoming message into exactly ONE of these categories:
- sales: interested in buying, pricing questions, demo requests, product inquiries
- support: existing customer with a problem, bug report, help request, account issue
- partnership: collaboration proposals, affiliate requests, integration inquiries, B2B
- spam: irrelevant, promotional, bot-generated, or malicious content

Respond ONLY with a JSON object in this exact format, no other text:
{
  "category": "sales|support|partnership|spam",
  "confidence": "high|medium|low",
  "reasoning": "one sentence explanation"
}"""

def classify_message(name: str, email: str, message: str) -> dict:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=256,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Name: {name}\nEmail: {email}\nMessage: {message}"
        }]
    )
    return json.loads(response.content[0].text)
```

### Slack Sender (slack.py)

```python
import requests
import os

CHANNEL_MAP = {
    "sales":       ("SLACK_SALES_WEBHOOK",       "#sales"),
    "support":     ("SLACK_SUPPORT_WEBHOOK",     "#support"),
    "partnership": ("SLACK_PARTNERSHIP_WEBHOOK", "#partnerships"),
    "spam":        ("SLACK_SPAM_WEBHOOK",         "#spam-archive"),
}

def post_to_slack(category: str, name: str, email: str, message: str, reasoning: str) -> bool:
    env_key, channel = CHANNEL_MAP.get(category, ("SLACK_SALES_WEBHOOK", "#sales"))
    webhook_url = os.getenv(env_key)
    if not webhook_url:
        return False

    payload = {
        "text": f"*New {category.upper()} message* → routed to {channel}",
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*New contact form submission — classified as `{category}`*"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Name:*\n{name}"},
                    {"type": "mrkdwn", "text": f"*Email:*\n{email}"}
                ]
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Message:*\n{message}"}
            },
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": f"AI reasoning: {reasoning}"}]
            }
        ]
    }
    response = requests.post(webhook_url, json=payload)
    return response.status_code == 200
```

### CORS Configuration (main.py)

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)
```

---

## Frontend — Key Implementation Details

### Vite Proxy (vite.config.js)

Always proxy `/api` to the backend so there are no CORS issues in dev:

```js
export default {
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
}
```

### Form State (App.jsx)

```jsx
const [status, setStatus] = useState('idle') // idle | loading | success | error
const [result, setResult] = useState(null)

const handleSubmit = async (formData) => {
  setStatus('loading')
  try {
    const { data } = await axios.post('/api/classify', formData)
    setResult(data)
    setStatus('success')
  } catch {
    setStatus('error')
  }
}
```

### Result Panel — Category Colors

| Category    | Background | Text    | Label       |
|-------------|------------|---------|-------------|
| sales       | #E1F5EE    | #085041 | 💼 Sales    |
| support     | #E6F1FB    | #0C447C | 🛠 Support  |
| partnership | #FAEEDA    | #633806 | 🤝 Partnership |
| spam        | #FAECE7    | #712B13 | 🚫 Spam     |

---

## Coding Conventions

- **Python:** snake_case, type hints on all functions, Pydantic models for all request/response bodies
- **React:** functional components only, no class components, props destructured in function signature
- **No inline styles in React** — use Tailwind utility classes only
- **Error handling:** all API calls wrapped in try/except (Python) and try/catch (JS)
- **Loading states:** always show a spinner or disabled button while awaiting API response
- **Never commit .env** — it is in .gitignore

---

## Running the Project

```bash
# Terminal 1 — Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
# Opens at http://localhost:5173
```

---

## Testing Without Real Slack Webhooks

If Slack webhooks are not yet set up, the backend should still work. In `slack.py`,
if the webhook URL is missing from `.env`, log a warning and return `slack_posted: false`
in the response — do not throw an error. The UI should display the classification
result regardless of whether Slack posting succeeded.

---

## Deployment Plan (after local build is complete)

| Layer    | Free Platform       | Notes                            |
|----------|---------------------|----------------------------------|
| Frontend | Vercel              | Connect GitHub repo, auto-deploy |
| Backend  | Railway or Render   | Add .env vars in dashboard       |
| Domain   | portfolio subdomain | e.g. router.pratibha.dev         |

After deploying, update CORS in `main.py` to allow the Vercel domain in addition
to localhost.

---

## Portfolio Context

This is Project #1 of 13 AI-powered applications being built for a career
transition portfolio from Senior Frontend Developer to AI Developer.

Developer: Pratibha  
Stack expertise: React, Angular, 16 years IT experience, 2+ years Gen AI  
Portfolio site: https://pratibharepos1.github.io/crafted-by-pratibha/

When suggesting improvements, keep code clean and well-commented — this project
will be shown to hiring managers and used as a live demo during interviews.
