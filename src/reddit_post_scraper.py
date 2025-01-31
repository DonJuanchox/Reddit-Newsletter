import requests
import re
import mimetypes
import logging

class RedditPost:
    def __init__(self, title, score, url):
        self.title = title
        self.score = score
        self.url = url
        self.content = None

    def __str__(self):
        content_preview = self.content[:100] + "..." if self.content else "No content fetched"
        return f"{self.title} ({self.score} upvotes)\n{self.url}\n{content_preview}"

    @staticmethod
    def is_image_url(url):
        """Check if a URL is an image using MIME type."""
        guessed_type, _ = mimetypes.guess_type(url)
        return guessed_type and guessed_type.startswith("image")

    def fetch_post(self):
        """Fetch the post content from the URL."""
        try:
            if self.is_image_url(self.url):
                self.content = "Skipped image content."
                return

            response = requests.get(self.url, timeout=10)
            response.raise_for_status()

            content_match = re.search(r'<div class="text-neutral-content" slot="text-body">(.*?)</div>', response.text, re.DOTALL)
            self.content = re.sub(r'<.*?>', '', content_match.group(1)).strip() if content_match else self.url

        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch content: {e}")
            self.content = f"Failed to fetch content: {e}"

    def read_post(self):
        """Return cleaned post content."""
        return re.sub(r'\s+', ' ', self.content.strip()) if self.content else "No content available"
