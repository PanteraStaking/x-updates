import requests
import logging

logger = logging.getLogger(__name__)

def send_to_telegram(tweet, topic_id, token, group_id):
    """Send a tweet to a specific topic in a Telegram group"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    # Format message
    message = f"<b>New post from @{tweet['account']}</b>\n\n"
    message += tweet['text']
    message += f"\n\n{tweet['url']}"
    
    payload = {
        "chat_id": group_id,
        "message_thread_id": topic_id,  # This specifies which topic to post to
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    
    try:
        response = requests.post(url, data=payload)
        response_json = response.json()
        
        if not response_json.get('ok'):
            logger.error(f"Failed to send to Telegram: {response_json}")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Error sending to Telegram: {str(e)}")
        return False