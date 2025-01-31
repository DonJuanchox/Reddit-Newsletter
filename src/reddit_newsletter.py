import os
import logging
import requests
import validators
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
import praw

# Import modules assuming they are available via PYTHONPATH
from Email_access import Email_Access
from reddit_post_scraper import RedditPost
from html_element import HTMLElement


def initialize_praw():
    """Load environment variables and initialize PRAW Reddit instance."""
    load_dotenv()

    required_vars = ["CLIENT_ID", "CLIENT_SECRET", "REDDIT_USERNAME", "REDDIT_PASSWORD", "USER_AGENT"]
    env_vars = {var: os.getenv(var) for var in required_vars}

    missing_vars = [key for key, value in env_vars.items() if not value]
    if missing_vars:
        logging.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        exit(1)

    return praw.Reddit(
        client_id=env_vars["CLIENT_ID"],
        client_secret=env_vars["CLIENT_SECRET"],
        user_agent=env_vars["USER_AGENT"],
        username=env_vars["REDDIT_USERNAME"],
        password=env_vars["REDDIT_PASSWORD"]
    )

def fetch_top_posts(subreddit_name, limit=30, min_score=50):
    """Fetch and return top posts from a subreddit."""
    try:
        reddit = initialize_praw()
        subreddit = reddit.subreddit(subreddit_name)

        logging.info(f"Fetching top {limit} posts from r/{subreddit_name}...")
        posts = [
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

def create_email_content(posts):
    """Generate HTML content for the email."""
    all_content = ""
    unwanted_phrases = ["Skipped image content.", "https://www.reddit.com/gallery"]

    for post in posts:
        div = HTMLElement("div", class_="container")
        title = HTMLElement("h1", HTMLElement("a", post.title, href=post.url, style="color: black !important; text-decoration: none;"))
        div.add_child(title)

        content = post.read_post()
        if any(phrase in content for phrase in unwanted_phrases):
            continue

        content_element = HTMLElement(
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
outlook = Email_Access()
subreddits = ['stocks', 'investing', 'StockMarket', 'wallstreetbets', 'ETFs_Europe', 'ValueInvesting']
all_posts = [post for sub in subreddits for post in fetch_top_posts(sub, limit=10, min_score=20)]
email_content = create_email_content(all_posts)
try:
    logging.info("Sending email...")
    outlook.send_email(
        'juannrodriguezpeinado@hotmail.com',
        'Reddit Top Posts | Juan Rodriguez',
        email_content,  
        html_body=True
    )
    logging.info("Email sent successfully!")
except Exception as e:
    logging.exception(f"Failed to send email: {e}")