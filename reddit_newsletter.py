"""
This module automates the process of fetching top Reddit posts from specified subreddits, formatting the content into an HTML email, and sending it via email.

The module performs the following tasks:
- Loads authentication credentials from environment variables.
- Initializes a PRAW Reddit instance using a decorator function.
- Fetches top posts from specified subreddits based on score and time filters.
- Extracts and cleans post content for inclusion in an email.
- Dynamically generates structured HTML content from the fetched posts.
- Sends the formatted email using an email client.

Example Usage:
    # The script fetches posts, formats them, and sends an email automatically.
    python script.py

This module is useful for automating the retrieval of Reddit content and distributing it via email for tracking trends or news aggregation.
"""

import os
import logging
import validators
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
import praw
from praw.reddit import Reddit
from praw.models import Subreddit

# Import modules assuming they are available via PYTHONPATH
from automatic_email import Email_Access
from reddit_post_scraper import RedditPost
from html_element import HTMLElement

# Load environment variables once
load_dotenv()
required_vars = ["CLIENT_ID", "CLIENT_SECRET", "REDDIT_USERNAME", "REDDIT_PASSWORD", "USER_AGENT", "E_SENDER", "E_PSWD"]
env_vars: dict[str, str | None] = {var: os.getenv(var) for var in required_vars}

missing_vars: list[str] = [key for key, value in env_vars.items() if not value]
if missing_vars:
    logging.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    exit(1)

def initialize_praw(func):
    """
    Decorator to initialize PRAW Reddit instance before executing a function.
    Loads authentication details from environment variables and passes the Reddit instance
    and environment variables to the decorated function.
    """
    def wrapper(*args, **kwargs):
        praw_instance = praw.Reddit(
            client_id=env_vars["CLIENT_ID"],
            client_secret=env_vars["CLIENT_SECRET"],
            user_agent=env_vars["USER_AGENT"],
            username=env_vars["REDDIT_USERNAME"],
            password=env_vars["REDDIT_PASSWORD"]
        )
        return func(praw_instance, env_vars, *args, **kwargs)
    return wrapper

@initialize_praw
def fetch_top_posts(reddit: Reddit, env_vars: dict, subreddit_name: str, limit: int = 30, min_score: int = 50) -> list[RedditPost]:
    """
    Fetch and return top posts from a subreddit.
    
    Args:
        reddit (Reddit): An initialized Reddit instance.
        env_vars (dict): Dictionary containing environment variables.
        subreddit_name (str): The subreddit from which to fetch posts.
        limit (int, optional): The maximum number of posts to retrieve. Defaults to 30.
        min_score (int, optional): The minimum score required for a post to be included. Defaults to 50.

    Returns:
        list[RedditPost]: A list of RedditPost objects containing post details.
    """
    try:
        subreddit: Subreddit = reddit.subreddit(subreddit_name)
        logging.info(f"Fetching top {limit} posts from r/{subreddit_name}...")
        posts: list[RedditPost] = [
            RedditPost(sub.title, sub.score, sub.url)
            for sub in subreddit.top(time_filter="day", limit=limit)
            if sub.score > min_score
        ]
        for post in posts:
            post.fetch_post()
        logging.info(f"Fetched {len(posts)} posts from r/{subreddit_name}.")
        return posts
    except Exception as e:
        logging.exception(f"Error fetching posts from r/{subreddit_name}: {e}")
        return []

def create_email_content(posts: list[RedditPost]) -> str:
    """
    Generate formatted HTML content for the email.
    
    Args:
        posts (list[RedditPost]): A list of RedditPost objects.
    
    Returns:
        str: A formatted HTML string ready to be sent via email.
    """
    all_content: str = ""
    unwanted_phrases: list[str] = ["Skipped image content.", "https://www.reddit.com/gallery"]
    for post in posts:
        div: HTMLElement = HTMLElement("div", class_="container")
        title: HTMLElement = HTMLElement(
            "h1", HTMLElement("a", post.title, href=post.url, style="color: black !important; text-decoration: none;")
        )
        div.add_child(title)
        content: str = post.read_post()
        if any(phrase in content for phrase in unwanted_phrases):
            continue
        content_element: HTMLElement = HTMLElement(
            "p",
            HTMLElement("a", content, href=content, style="color: #FF4500 !important; text-decoration: none; font-weight: bold;")
        ) if validators.url(content) else HTMLElement("p", content)
        div.add_child(content_element)
        div.add_child(HTMLElement("br"))
        div.add_child(HTMLElement("br"))
        all_content += str(div)
    return f"""
    <style>
        .container {{ font-family: Arial, sans-serif; margin-bottom: 20px; }}
        h1 {{ font-size: 30px; margin: 0; color: black; }}
        h1 a {{ color: black !important; text-decoration: none; font-weight: normal; }}
        p {{ font-size: 14px; margin: 5px 0; }}
        a {{ color: #FF4500 !important; text-decoration: none; font-weight: bold; }}
    </style>
    {all_content}
    """

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

subreddits: list[str] = ['stocks', 'investing', 'StockMarket', 'wallstreetbets', 'ETFs_Europe', 'ValueInvesting']
all_posts: list[RedditPost] = [
    post for sub in subreddits 
    for post in fetch_top_posts(subreddit_name=sub, limit=50, min_score=20)
]
email_content: str = create_email_content(all_posts)

outlook = Email_Access(
    imap_server="imap.gmail.com",
    smtp_server="smtp.gmail.com",
    email_user=env_vars["E_SENDER"],
    email_pass=env_vars["E_PSWD"]
)

try:
    logging.info("Sending email...")
    outlook.send_email(
        '--',
        'Reddit Top Posts | Juan Rodriguez',
        email_content,
        html_body=True
    )
    logging.info("Email sent successfully!")
except Exception as e:
    logging.exception(f"Failed to send email: {e}")
