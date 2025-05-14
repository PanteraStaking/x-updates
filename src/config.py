import os
import dotenv

# Load .env file if it exists
dotenv.load_dotenv()

def load_config():
    """Load configuration from environment variables"""
    config = {
        'telegram_token': os.environ.get('TELEGRAM_BOT_TOKEN'),
        'telegram_group_id': os.environ.get('TELEGRAM_GROUP_ID'),
        'twitter': {
            'api_key': os.environ.get('X_API_KEY'),
            'api_secret': os.environ.get('X_API_SECRET'),
            'access_token': os.environ.get('X_ACCESS_TOKEN'),
            'access_secret': os.environ.get('X_ACCESS_SECRET')
        },
        'accounts': {
            # X account : Telegram topic ID
            "oraichain": os.environ.get('ORAICHAIN_TOPIC_ID'),
            "babylonlabs_io": os.environ.get('BABYLON_TOPIC_ID')
        }
    }
    
    # Validation checks
    if not config['telegram_token']:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN environment variable")
        
    if not config['telegram_group_id']:
        raise ValueError("Missing TELEGRAM_GROUP_ID environment variable")
        
    if not all(config['twitter'].values()):
        raise ValueError("Missing Twitter API credentials")
        
    if not all(config['accounts'].values()):
        raise ValueError("Missing Telegram topic IDs")
    
    return config