"""
Email tool - searches the connected Gmail account (Gmail API, via
gmail_auth_service.py for credentials). This is deliberately a separate
category from live_data_service.py: email is private, per-user data,
not public "live web" data - see planner_service.py's needs_email flag.
"""

from googleapiclient.discovery import build

from backend.app.services.gmail_auth_service import get_credentials


def search_emails(session_id, query, max_results=5):
    credentials = get_credentials(session_id)

    if not credentials:
        return "Gmail isn't connected for this session. Connect it via /auth/gmail/connect first."

    try:
        service = build("gmail", "v1", credentials=credentials)

        # Gmail's search syntax (e.g. "from:vendor subject:invoice") works
        # directly as `query` here - no translation needed.
        response = service.users().messages().list(
            userId="me", q=query, maxResults=max_results
        ).execute()

        message_refs = response.get("messages", [])

        if not message_refs:
            return "No matching emails found."

        summaries = []

        for ref in message_refs:
            message = service.users().messages().get(
                userId="me", id=ref["id"], format="metadata",
                metadataHeaders=["From", "Subject", "Date"],
            ).execute()

            headers = {h["name"]: h["value"] for h in message["payload"].get("headers", [])}
            snippet = message.get("snippet", "")

            summaries.append(
                f"From: {headers.get('From', 'unknown')}\n"
                f"Subject: {headers.get('Subject', '(no subject)')}\n"
                f"Date: {headers.get('Date', '')}\n"
                f"Preview: {snippet}"
            )

        return "\n\n".join(summaries)

    except Exception as e:
        return f"Email search failed: {e}"
