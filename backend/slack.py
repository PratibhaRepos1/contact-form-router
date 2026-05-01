import logging
import os
import requests

logger = logging.getLogger(__name__)

CHANNEL_MAP = {
    "sales":       ("SLACK_SALES_WEBHOOK",       "#sales"),
    "support":     ("SLACK_SUPPORT_WEBHOOK",     "#support"),
    "partnership": ("SLACK_PARTNERSHIP_WEBHOOK", "#partnerships"),
    "spam":        ("SLACK_SPAM_WEBHOOK",        "#spam-archive"),
}


def channel_for(category: str) -> str:
    return CHANNEL_MAP.get(category, ("SLACK_SALES_WEBHOOK", "#sales"))[1]


def post_to_slack(category: str, name: str, email: str, message: str, reasoning: str) -> bool:
    env_key, channel = CHANNEL_MAP.get(category, ("SLACK_SALES_WEBHOOK", "#sales"))
    webhook_url = os.getenv(env_key)
    if not webhook_url:
        logger.warning("Missing webhook for category=%s (env var %s); skipping Slack post", category, env_key)
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
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        return response.status_code == 200
    except requests.RequestException as exc:
        logger.error("Slack post failed for %s: %s", category, exc)
        return False
