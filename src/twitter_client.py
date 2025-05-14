import requests
import logging
import time
from requests_oauthlib import OAuth1
from src.storage import get_cached_user_ids, save_user_id

logger = logging.getLogger(__name__)

def get_twitter_api_v2_auth(config):
    """Create OAuth1 authentication for X/Twitter API v2"""
    return OAuth1(
        config['twitter']['api_key'],
        config['twitter']['api_secret'],
        config['twitter']['access_token'],
        config['twitter']['access_secret']
    )

def get_new_tweets(account, processed_ids, config, max_retries=3):
    """Get new tweets from specified account using Twitter API v2 with retry logic"""
    auth = get_twitter_api_v2_auth(config)
    new_tweets = []
    
    # Check for cached user ID first
    cached_ids = get_cached_user_ids()
    user_id = cached_ids.get(account)
    
    # Only look up user ID if not cached
    if not user_id:
        logger.info(f"No cached user ID for {account}, looking it up (uses 1 API call)")
        for attempt in range(max_retries):
            try:
                url = f"https://api.twitter.com/2/users/by/username/{account}"
                response = requests.get(url, auth=auth)
                
                if response.status_code != 200:
                    logger.error(f"Error getting user ID for {account}: {response.status_code} - {response.text}")
                    if "429" in str(response.status_code) and attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 5
                        logger.warning(f"Rate limited, waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    return []
                    
                user_data = response.json()
                if 'data' not in user_data:
                    logger.error(f"Unexpected response format for user {account}: {user_data}")
                    return []
                    
                user_id = user_data['data']['id']
                # Cache the user ID for future use
                save_user_id(account, user_id)
                logger.info(f"User ID for {account} cached: {user_id}")
                break
                
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 5
                    logger.warning(f"Rate limited, waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                logger.error(f"Error fetching user ID for {account}: {str(e)}")
                return []
    else:
        logger.info(f"Using cached user ID for {account}: {user_id}")
    
    # If we still don't have a user ID, return empty list
    if not user_id:
        return []
        
    # Get recent tweets from this user (uses another API call)
    logger.info(f"Fetching tweets for {account} (uses 1 API call)")
    for attempt in range(max_retries):
        try:
            tweets_url = f"https://api.twitter.com/2/users/{user_id}/tweets"
            params = {
                "tweet.fields": "created_at,text",
                "max_results": 5
            }
        
            tweets_response = requests.get(tweets_url, auth=auth, params=params)
            
            if tweets_response.status_code != 200:
                logger.error(f"Error fetching tweets for {account}: {tweets_response.status_code} - {tweets_response.text}")
                if "429" in str(tweets_response.status_code) and attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 5
                    logger.warning(f"Rate limited, waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                return []
                
            tweets_data = tweets_response.json()
            
            if 'data' not in tweets_data:
                logger.info(f"No tweets found for {account} or unexpected response format: {tweets_data}")
                return []
            
            for tweet in tweets_data['data']:
                tweet_id = tweet['id']
                
                # Skip if we've already processed this tweet
                if tweet_id in processed_ids:
                    continue
                    
                # Format tweet data with x.com URL
                tweet_data = {
                    'id': tweet_id,
                    'text': tweet['text'],
                    'account': account,
                    'url': f"https://x.com/{account}/status/{tweet_id}"
                }
                
                new_tweets.append(tweet_data)
                
            return new_tweets
            
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 5
                logger.warning(f"Rate limited, waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue
            logger.error(f"Error fetching tweets for {account}: {str(e)}")
            return []
    
    return []