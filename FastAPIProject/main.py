import os
import base64
import re
from email import message_from_bytes
from email.message import EmailMessage
from email.policy import default
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from bs4 import BeautifulSoup
from pydantic import BaseModel


# ================= CONFIG =================

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify"
]

PROCESSED_LABEL = "PROCESSED_BY_BOT"


# ================= MODELS =================

class Article(BaseModel):
    title: str
    body: Optional[str]
    image: Optional[str]
    link: str


# ================= HELPERS =================

def strip_source_param(url: str) -> str:
    return url.split("?source=")[0] if "?source=" in url else url


def is_noise_link(url: str) -> bool:
    path = url.replace("https://medium.com", "").replace("http://medium.com", "")
    if not path.startswith("/@"):
        return True
    if re.fullmatch(r"/@[^/]+", path):
        return True
    return path.startswith((
        "/me", "/settings", "/new-story", "/m/signin",
        "/m/account", "/m/notifications", "/membership",
        "/about", "/jobs", "/help", "/plans"
    ))


def extract_image_near(anchor):
    for img in (
        anchor.find("img"),
        anchor.parent.find("img") if anchor.parent else None,
        anchor.find_previous("img")
    ):
        if img:
            return (
                img.get("src")
                or img.get("data-src")
                or (img.get("srcset", "").split(" ")[0] if img.get("srcset") else None)
            )
    return None


def extract_articles_from_medium_email(raw_bytes: bytes):
    msg = message_from_bytes(raw_bytes, policy=default)

    html = None
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            payload = part.get_payload(decode=True)
            if payload:
                html = payload.decode(errors="ignore")
                break

    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    articles = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "medium.com" not in href:
            continue

        href = strip_source_param(href)
        if is_noise_link(href):
            continue

        title = a.get_text(strip=True)
        if not title:
            continue

        image = extract_image_near(a)
        body = ""
        p = a.find_next("p")
        if p:
            body = p.get_text(strip=True)

        articles.append((title, href, image, body))

    return articles


def mark_processed(service, msg_id):
    service.users().messages().modify(
        userId="me",
        id=msg_id,
        body={"addLabelIds": [PROCESSED_LABEL]}
    ).execute()


# ================= MAIN =================

def main():
    # Load OAuth token from GitHub secret
    if "GMAIL_TOKEN" not in os.environ:
        raise RuntimeError("Missing GMAIL_TOKEN secret")


    import json

    token_data = json.loads(os.environ["GMAIL_TOKEN"])
    with open("token.json", "w") as f:
        json.dump(token_data, f)

    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    service = build("gmail", "v1", credentials=creds)

    query = f"from:medium newer_than:1d -label:{PROCESSED_LABEL}"
    results = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=10
    ).execute()

    messages = results.get("messages", [])
    if not messages:
        print("No new Medium emails.")
        return

    seen_links = set()
    html_blocks = []

    for m in messages:
        msg_data = service.users().messages().get(
            userId="me",
            id=m["id"],
            format="raw"
        ).execute()

        raw_bytes = base64.urlsafe_b64decode(msg_data["raw"])
        articles = extract_articles_from_medium_email(raw_bytes)

        for title, link, image, body in articles:
            if link in seen_links:
                continue
            seen_links.add(link)

            article = Article(
                title=title,
                body=body,
                image=image,
                link=f"https://freedium-mirror.cfd/{link}"
            )

            html_blocks.append(f"""
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:32px;">
              <tr>
                <td style="font-family:Arial,sans-serif;">
                  {f"<img src='{article.image}' width='100%' style='border-radius:6px;margin-bottom:16px;'>" if article.image else ""}
                  <a href="{article.link}" style="text-decoration:none;color:#000;">
                    <h2 style="margin:0 0 8px;font-size:22px;line-height:1.3;">
                      {article.title}
                    </h2>
                  </a>
                  <p style="margin:0;font-size:15px;line-height:1.6;color:#555;">
                    {article.body or ""}
                  </p>
                </td>
              </tr>
            </table>
            """)

        mark_processed(service, m["id"])

    if not html_blocks:
        print("No articles extracted.")
        return

    email = EmailMessage()
    email["to"] = "dineshthumma15@gmail.com"
    email["from"] = "me"
    email["subject"] = "Today's Medium Articles"
    email.add_alternative(
        "<h1 style='font-family:Arial;'>Today's Medium Articles</h1>" + "".join(html_blocks),
        subtype="html"
    )

    encoded = base64.urlsafe_b64encode(email.as_bytes()).decode()
    service.users().messages().send(
        userId="me",
        body={"raw": encoded}
    ).execute()

    print("Email sent successfully.")


if __name__ == "__main__":
    main()
