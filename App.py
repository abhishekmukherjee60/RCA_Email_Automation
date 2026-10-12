import email
import imaplib
import re
from datetime import datetime, timedelta
from email.header import decode_header
from bs4 import BeautifulSoup
from google import genai

# ============================================================
# 1. CONFIGURATION
# ============================================================
EMAIL_USER = "abhishek.mukherjee@mpokket.com"
EMAIL_PASS = "hvwk hesb wvwr dwzk"  # Gmail App Password
GEMINI_API_KEY = "AQ.Ab8RN6IQGpOKCxWms9eQWDb5yYVfzulB3-8BkCI9ong6padc8w"  # Replace with your actual key

ai_client = genai.Client(api_key=GEMINI_API_KEY)


# ============================================================
# 2. EXTRACTION METHODS
# ============================================================
def extract_phone_with_regex(raw_html_or_text: str) -> str:
    """PRIMARY METHOD: Strips HTML using BeautifulSoup and applies Regex."""
    if not raw_html_or_text:
        return ""

    soup = BeautifulSoup(raw_html_or_text, "html.parser")
    clean_text = soup.get_text(" ", strip=True)

    # Search for standard Indian 10-digit mobile numbers (starting with 6, 7, 8, or 9)
    phones = re.findall(r"(?<!\d)[6-9]\d{9}(?!\d)", clean_text)

    if phones:
        return phones[0]
    return ""


def extract_phone_with_gemini(email_text: str) -> str:
    """SECONDARY METHOD: Uses Gemini LLM if Regex fails."""
    prompt = (
        """
You are an information extraction assistant.

Read the email below.
Find the target 10-digit Indian mobile phone number mentioned in the RCA request.

Return ONLY the 10 digits with no spaces, hyphens, country codes, or additional text.
If no phone number is present, return NONE.

Email Content:
"""
        + email_text
    )

    try:
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        result = response.text.strip()

        match = re.search(r"(?<!\d)[6-9]\d{9}(?!\d)", result)
        return match.group(0) if match else "NONE"
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return "NONE"


# ============================================================
# 3. HELPER FUNCTIONS
# ============================================================
def decode_subject(subject: str) -> str:
    if not subject:
        return ""
    decoded_parts = decode_header(subject)
    subject_text = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            subject_text += part.decode(encoding or "utf-8", errors="ignore")
        else:
            subject_text += part
    return subject_text


def extract_email_body(msg) -> str:
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if "attachment" in content_disposition.lower():
                continue

            if content_type in ["text/html", "text/plain"]:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    body = payload.decode(charset, errors="ignore")
                    if content_type == "text/html":
                        break
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            body = payload.decode(charset, errors="ignore")

    return body


# ============================================================
# 4. FETCH YESTERDAY'S EMAILS FROM 'rca' LABEL
# ============================================================
def fetch_yesterday_rca_emails():
    mail = None
    try:
        today = datetime.now()
        yesterday = today - timedelta(days=1)

        after_date = yesterday.strftime("%Y/%m/%d")
        before_date = today.strftime("%Y/%m/%d")

        print("Connecting to Gmail...")
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_USER, EMAIL_PASS)
        print("Login successful.")

        print("\nSelecting 'rca' label...")
        status, data = mail.select("rca", readonly=True)

        if status != "OK":
            print("\n❌ Could not select 'rca'. Please check label name.")
            return

        search_query = f"after:{after_date} before:{before_date}"
        print(
            f"\nSearching for emails received yesterday ({yesterday.strftime('%d-%b-%Y')}) using query: '{search_query}'..."
        )

        status, messages = mail.uid("SEARCH", None, "X-GM-RAW", search_query)

        if status != "OK":
            print("\n❌ Gmail search failed.")
            return

        email_ids = messages[0].split()

        if not email_ids:
            print(
                f"\nNo emails found in 'rca' label for yesterday ({yesterday.strftime('%d-%b-%Y')})."
            )
            return

        print(f"\nFound {len(email_ids)} email(s) received yesterday.\n")

        for e_id in email_ids:
            print("=" * 60)
            status, msg_data = mail.uid("FETCH", e_id, "(RFC822)")

            if status != "OK":
                continue

            for response_part in msg_data:
                if not isinstance(response_part, tuple):
                    continue

                msg = email.message_from_bytes(response_part[1])
                subject = decode_subject(msg.get("Subject"))
                sender = msg.get("From")
                date_str = msg.get("Date")
                raw_body = extract_email_body(msg)

                print(f"Subject: {subject}")
                print(f"From:    {sender}")
                print(f"Date:    {date_str}")

                if not raw_body:
                    print("⚠️ Email body is empty.")
                    continue

                # --------------------------------------------------
                # STEP 1: PRIMARY EXTRACTION (BeautifulSoup + Regex)
                # --------------------------------------------------
                phone_number = extract_phone_with_regex(raw_body)
                extraction_method = "Primary (BeautifulSoup + Regex)"

                # --------------------------------------------------
                # STEP 2: SECONDARY EXTRACTION (Gemini Fallback)
                # --------------------------------------------------
                if not phone_number:
                    print(
                        "--> Regex failed. Switching to Gemini (Secondary)..."
                    )
                    soup = BeautifulSoup(raw_body, "html.parser")
                    clean_text = soup.get_text(" ", strip=True)

                    phone_number = extract_phone_with_gemini(clean_text)
                    extraction_method = "Secondary (Gemini AI)"

                print(f"\n➡ Extracted Phone Number: {phone_number}")
                print(f"➡ Extraction Method Used: {extraction_method}")
                print("-" * 60)

        print("\n✅ Processing completed.")

    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__} - {str(e)}")

    finally:
        if mail:
            try:
                mail.logout()
            except Exception:
                pass


if __name__ == "__main__":
    fetch_yesterday_rca_emails()