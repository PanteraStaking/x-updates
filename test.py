import logging
from src.config import load_config
import tweepy
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_twitter_connection(config):
    """Test connection to Twitter API"""
    try:
        auth = tweepy.OAuth1UserHandler(
            config['twitter']['api_key'],
            config['twitter']['api_secret'],
            config['twitter']['access_token'],
            config['twitter']['access_secret']
        )
        api = tweepy.API(auth)
        
        # Test with a simple API call
        user = api.verify_credentials()
        logger.info(f"✅ Twitter connection successful! Authenticated as: {user.screen_name}")
        return True
    except Exception as e:
        logger.error(f"❌ Twitter connection failed: {str(e)}")
        return False

def test_telegram_connection(config):
    """Test connection to Telegram API"""
    try:
        url = f"https://api.telegram.org/bot{config['telegram_token']}/getMe"
        response = requests.get(url)
        data = response.json()
        
        if data.get('ok'):
            bot_info = data.get('result', {})
            logger.info(f"✅ Telegram connection successful! Bot name: {bot_info.get('first_name')}")
            return True
        else:
            logger.error(f"❌ Telegram connection failed: {data}")
            return False
    except Exception as e:
        logger.error(f"❌ Telegram connection failed: {str(e)}")
        return False

def main():
    logger.info("Testing API connections...")
    
    try:
        config = load_config()
        twitter_ok = test_twitter_connection(config)
        telegram_ok = test_telegram_connection(config)
        
        if twitter_ok and telegram_ok:
            logger.info("All connections successful! Your environment is properly configured.")
        else:
            logger.warning("Some connections failed. Check the logs above.")
    except Exception as e:
        logger.error(f"Configuration error: {str(e)}")

if __name__ == "__main__":
    main()