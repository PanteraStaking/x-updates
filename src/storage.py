import json
import os
import logging

logger = logging.getLogger(__name__)

# File to store processed tweet IDs
PROCESSED_TWEETS_FILE = "processed_tweets.json"

USER_IDS_FILE = "user_ids.json"

def get_processed_tweets():
    """Load previously processed tweets"""
    if os.path.exists(PROCESSED_TWEETS_FILE):
        try:
            with open(PROCESSED_TWEETS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading processed tweets: {str(e)}")
    
    return {}

def save_processed_tweets(processed_tweets):
    """Save processed tweets to file"""
    try:
        with open(PROCESSED_TWEETS_FILE, 'w') as f:
            json.dump(processed_tweets, f)
        return True
    except Exception as e:
        logger.error(f"Error saving processed tweets: {str(e)}")
        return False

def get_cached_user_ids():
    """Load cached user IDs"""
    if os.path.exists(USER_IDS_FILE):
        try:
            with open(USER_IDS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading cached user IDs: {str(e)}")
    return {}

def save_user_id(account, user_id):
    """Save a user ID to cache"""
    user_ids = get_cached_user_ids()
    user_ids[account] = user_id
    try:
        with open(USER_IDS_FILE, 'w') as f:
            json.dump(user_ids, f)
        return True
    except Exception as e:
        logger.error(f"Error saving user ID: {str(e)}")
        return False