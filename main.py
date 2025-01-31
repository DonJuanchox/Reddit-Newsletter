import os
import sys
import logging
import validators
import requests

from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
import praw


sys.path.insert(0, 'C:\\Users\\juann\\OneDrive\\Documentos\\GitHub\\OOP\\Automatic Email\\src')
from Email_access import Email_Access
from rdtt_post import RedditPost
from web_builder import HTMLElement  # Assuming you have an HTMLElement class

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load credentials from environment variables
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
USER_AGENT = os.getenv("USER_AGENT")

# Validate environment variables
if not all([CLIENT_ID, CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD, USER_AGENT]):
    logging.error("Missing required environment variables.")
    exit(1)

def get_reddit_access_token(client_id, client_secret, username, password, user_agent):
    """Authenticate with Reddit and return an access token."""
    auth = HTTPBasicAuth(client_id, client_secret)
    data = {
        "grant_type": "password",
        "username": username,
        "password": password
    }
    headers = {"User-Agent": user_agent}

    try:
        response = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=auth,
            data=data,
            headers=headers
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()["access_token"]
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to get access token: {e}")
        return None

def initialize_praw(client_id, client_secret, user_agent, access_token):
    """Initialize and return a PRAW Reddit instance."""
    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
        token=access_token
    )

def fetch_top_posts(subreddit_name, limit=30, min_score=50):
    """Fetch and display top posts from a subreddit."""
    access_token = get_reddit_access_token(CLIENT_ID, CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD, USER_AGENT)
    if not access_token:
        logging.error("Authentication failed. Exiting.")
        return []

    reddit = initialize_praw(CLIENT_ID, CLIENT_SECRET, USER_AGENT, access_token)
    subreddit = reddit.subreddit(subreddit_name)

    logging.info(f"Top {limit} posts in r/{subreddit.display_name}.")
    output = []
    for submission in subreddit.top(time_filter="day", limit=limit):
        if submission.score > min_score:
            reddit_post = RedditPost(submission.title, submission.score, submission.url)
            reddit_post.fetch_post()
            output.append(reddit_post)
    return output

import validators

def create_email_content(posts):
    """Create HTML content for the email."""
    all_content = ''
    unwanted_phrases = ['Skipped image content.', 'https://www.reddit.com/gallery']

    def is_url(string):
        return validators.url(string)  # Returns True if the string is a URL

    for post in posts:
        div = HTMLElement("div", class_="container")
        
        # Wrap the title inside an <a> tag but ensure it stays black
        title = HTMLElement("h1", 
            HTMLElement("a", post.title, href=post.url, style="color: black !important; text-decoration: none;")
        )
        div.add_child(title)

        # Get the post content
        content = post.read_post()

        # Check if content is an unwanted phrase
        if any(phrase in content for phrase in unwanted_phrases):
            continue
        elif is_url(content):  # If content is a URL, make it clickable and highlighted
            content_element = HTMLElement("p", 
                HTMLElement("a", content, href=content, style="color: #FF4500 !important; text-decoration: none; font-weight: bold;")
            )
        else:
            content_element = HTMLElement("p", content)

        # Add the content to the div
        div.add_child(content_element)

        # Add line breaks for spacing
        div.add_child(HTMLElement("br"))
        div.add_child(HTMLElement("br"))

        all_content += str(div)
    
    # Add styling to the HTML output
    styled_html = f"""
    <style>
        .container {{
            font-family: Arial, sans-serif;
            margin-bottom: 20px;
        }}
        h1 {{
            font-size: 30px;
            margin: 0;
            color: black;
        }}
        h1 a {{
            color: black !important;
            text-decoration: none;
            font-weight: normal;
        }}
        p {{
            font-size: 14px;
            margin: 5px 0;
        }}
        a {{
            color: #FF4500 !important;
            text-decoration: none;
            font-weight: bold;
        }}
    </style>
    {all_content}
    """
    return styled_html

# Main script
if __name__ == "__main__":
    outlook = Email_Access()

    sub_reddits = ['stocks', 'investing', 'StockMarket', 'wallstreetbets', 'ETFs_Europe', 'ValueInvesting']
    all_posts = []
    for sub in sub_reddits:
        posts = fetch_top_posts(sub, limit=100, min_score=20)
        all_posts += posts

    email_content = create_email_content(all_posts)

    logging.info("---------- Sending email... ----------")
    outlook.send_email(
        'juannrodriguezpeinado@hotmail.com',
        'Reddit Top Posts | Juan Rodriguez',
        email_content,  
        html_body=True
    )