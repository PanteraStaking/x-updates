#!/usr/bin/env python3

import logging
import time
import os
import sys
from datetime import datetime
from src.config import load_config
from src.twitter_client import get_new_tweets
from src.telegram_client import send_to_telegram
from src.storage import get_processed_tweets, save_processed_tweets

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Check for flags
    process_all = "--all" in sys.argv
    dry_run = "--dry-run" in sys.argv
    
    # Load configuration
    config = load_config()
    
    # Get previously processed tweets
    processed_tweets = get_processed_tweets()
    newly_processed = []
    
    # Get all accounts
    accounts = list(config['accounts'].items())
    
    # Create rotation file to track which account to process next
    rotation_file = "account_rotation.txt"
    
    # Figure out which account to process based on rotation
    if not process_all and len(accounts) > 1:
        try:
            if os.path.exists(rotation_file):
                with open(rotation_file, 'r') as f:
                    last_processed = f.read().strip()
                    current_index = next((i for i, (acct, _) in enumerate(accounts) if acct == last_processed), -1)
                    next_index = (current_index + 1) % len(accounts)
            else:
                next_index = 0
                
            # Just process one account this run (to stay within rate limits)
            accounts = [accounts[next_index]]
            
            # Update rotation file
            with open(rotation_file, 'w') as f:
                f.write(accounts[0][0])
            
            logger.info(f"Processing account {accounts[0][0]} (rotational mode)")
                
        except Exception as e:
            logger.error(f"Error with account rotation: {str(e)}")
    
    # Process each selected account
    for account, topic_id in accounts:
        logger.info(f"Checking for new tweets from {account}")
        
        # Get new tweets
        new_tweets = get_new_tweets(account, processed_tweets.get(account, []), config)
        
        if not new_tweets:
            logger.info(f"No new tweets from {account}")
            continue
            
        # Send each tweet to appropriate Telegram topic
        for tweet in new_tweets:
            group_id = config['telegram_group_id']
            logger.info(f"Sending tweet {tweet['id']} to topic {topic_id} in group {group_id}")
            
            if not dry_run:
                success = send_to_telegram(tweet, topic_id, config['telegram_token'], group_id)
            else:
                logger.info(f"DRY RUN - Would send tweet: {tweet['text'][:30]}...")
                success = True
            
            if success:
                # Track this tweet as processed
                if account not in processed_tweets:
                    processed_tweets[account] = []
                processed_tweets[account].append(tweet['id'])
                newly_processed.append((account, tweet['id']))
    
    # Save updated processed tweets
    if newly_processed:
        logger.info(f"Processed {len(newly_processed)} new tweets")
        save_processed_tweets(processed_tweets)
    else:
        logger.info("No new tweets to process")

if __name__ == "__main__":
    main()