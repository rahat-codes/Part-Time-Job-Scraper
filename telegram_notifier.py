import requests

def send_telegram_job(bot_token, chat_id, title, company, city, salary, url):
    """Sends a formatted job listing message to a Telegram chat/channel using HTML parsing."""
    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    # Format the message text with bold and code tags for high readability
    message_text = (
        f"<b>🚀 New Job Listing Scraped!</b>\n\n"
        f"📌 <b>Title:</b> {title}\n"
        f"🏢 <b>Company:</b> {company}\n"
        f"📍 <b>Location:</b> {city}\n"
        f"💰 <b>Salary:</b> ${salary:,}\n\n"
        f"🔗 <a href='{url}'>Apply Here</a>"
    )
    
    payload = {
        "chat_id": chat_id,
        "text": message_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    
    try:
        response = requests.post(api_url, json=payload)
        if response.status_code == 200:
            print(f"Notification sent for: {title} at {company}")
            return True
        else:
            print(f"Telegram API Error ({response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"Network error sending Telegram notification: {e}")
        return False
