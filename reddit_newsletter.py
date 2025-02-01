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

def initialize_praw() -> Reddit:
    """
    Load environment variables and initialize PRAW Reddit instance.

    This function loads Reddit API credentials from environment variables and initializes
    a PRAW (Python Reddit API Wrapper) instance for interacting with Reddit.

    Returns:
        Reddit: A PRAW Reddit instance for API interactions.

    Raises:
        SystemExit: If any required environment variable is missing.
    """
    load_dotenv()

    required_vars = ["CLIENT_ID", "CLIENT_SECRET", "REDDIT_USERNAME", "REDDIT_PASSWORD", "USER_AGENT"]
    env_vars: dict[str, str | None] = {var: os.getenv(var) for var in required_vars}

    missing_vars: list[str] = [key for key, value in env_vars.items() if not value]
    if missing_vars:
        logging.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        exit(1)

    return praw.Reddit(
        CLIENT_ID=env_vars["CLIENT_ID"],
        CLIENT_SECRET=env_vars["CLIENT_SECRET"],
        USER_AGENT=env_vars["USER_AGENT"],
        REDDIT_USERNAME=env_vars["REDDIT_USERNAME"],
        REDDIT_PASSWORD=env_vars["REDDIT_PASSWORD"]
    )

def fetch_top_posts(subreddit_name: str, limit: int = 30, min_score: int = 50) -> list[RedditPost]:
    """
    Fetch and return top posts from a subreddit.

    This function retrieves the top daily posts from a given subreddit, filtering
    out posts that do not meet the minimum upvote score.

    Args:
        subreddit_name (str): The name of the subreddit to fetch posts from.
        limit (int, optional): Maximum number of posts to retrieve. Default is 30.
        min_score (int, optional): Minimum score required for posts to be included. Default is 50.

    Returns:
        list[RedditPost]: A list of RedditPost objects containing post details.

    Logs:
        - INFO: Number of posts fetched.
        - ERROR: If an exception occurs while fetching posts.
    """
    try:
        reddit: Reddit = initialize_praw()
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

    This function creates an HTML email containing Reddit posts, formatting
    them with proper spacing and styles.

    Args:
        posts (list[RedditPost]): A list of RedditPost objects.

    Returns:
        str: A formatted HTML string ready to be sent via email.

    Notes:
        - Skips posts that contain unwanted phrases like "Skipped image content."
        - Converts URLs in the post body into clickable links.
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

outlook = Email_Access(
    imap_server="imap.gmail.com",   #  IMAP server for Gmail
    smtp_server="smtp.gmail.com",   #  SMTP server for Gmail
    email_user="fre792@gmail.com",  #  Your Gmail email
    email_pass="axgn hgay lhzi gepy"  #  Your Gmail App Password (not main password)
)

print("Email Sent Successfully!")

subreddits: list[str] = ['stocks', 'investing', 'StockMarket', 'wallstreetbets', 'ETFs_Europe', 'ValueInvesting']
all_posts: list[RedditPost] = [post for sub in subreddits for post in fetch_top_posts(sub, limit=10, min_score=20)]
email_content: str = create_email_content(all_posts)

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
