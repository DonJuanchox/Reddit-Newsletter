import praw
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup as bs

class RedditPost:
    def __init__(self, title, score, url):
        self.title = title
        self.score = score
        self.url = url
        self.content = None

    def __str__(self):
        content_preview = self.content[:100] + "..." if self.content else "No content fetched"
        return f"{self.title} ({self.score} upvotes)\n{self.url}\n{content_preview}"

    def fetch_post(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            soup = bs(response.text, "html.parser")
            
            # Extract and clean text from the specified HTML elements
            text_elements = soup.find_all("div", {"class": "text-neutral-content", "slot": "text-body"})
            if text_elements:
                text = "\n".join(element.get_text(separator=" ", strip=True) for element in text_elements)
                self.content = text
            else:
                self.content = "No relevant content found."
        except requests.exceptions.RequestException as e:
            self.content = f"Failed to fetch content: {e}"

    def read_post(self):
        return self.content

# Reddit API credentials
CLIENT_ID = "rEeXJSIKc8QR7kGlsxyoRQ"
CLIENT_SECRET = "OzFU6kY0oVmqry1ReRA-0tql2TCRhg"
REDIRECT_URI = "http://localhost:8080"
USER_AGENT = "email_threat/1.0 by Omegax74"

# Step 1: Get OAuth2 token
auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
data = {
    "grant_type": "password",
    "username": "Omegax74",  # Replace with your Reddit username
    "password": "Juanrod12."   # Replace with your Reddit password
}
headers = {"User-Agent": USER_AGENT}

response = requests.post(
    "https://www.reddit.com/api/v1/access_token",
    auth=auth,
    data=data,
    headers=headers
)

if response.status_code != 200:
    raise Exception(f"Failed to get access token: {response.text}")

access_token = response.json()["access_token"]

# Step 2: Initialize PRAW with OAuth2 token
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT,
    token=access_token
)


# Step 3: Fetch posts from a subreddit
subreddit = reddit.subreddit("stocks")
print(f"Top posts in r/{subreddit.display_name}:")
for submission in subreddit.top(time_filter="day", limit=5):
    if submission.score > 50:
        print(f"Title: {submission.title}")
        print(f"Score: {submission.score}")
        print(f"URL: {submission.url}")
        reddit_post = RedditPost(submission.title, submission.score, submission.url)
        reddit_post.fetch_post()
        print(reddit_post.read_post())



# print(f"Hot posts in r/{subreddit.display_name}:")
# for submission in subreddit.hot(time_filter="day", limit=50):
#     print(f"Title: {submission.title}")
#     print(f"Score: {submission.score}")
#     print(f"URL: {submission.url}")
#     print("-" * 40)
#         top_level_comments = list(submission.comments)
#         all_comments = submission.comments.list()
#         print("-" * 40)

# from praw.models import MoreComments
# for comment in all_comments:
#     if isinstance(top_level_comment, MoreComments):
#         continue
#     print(top_level_comment.body)