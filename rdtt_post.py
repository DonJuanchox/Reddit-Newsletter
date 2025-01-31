import requests
import re

class RedditPost:
    def __init__(self, title, score, url):
        self.title = title
        self.score = score
        self.url = url
        self.content = None

    def __str__(self):
        content_preview = self.content[:100] + "..." if self.content else "No content fetched"
        return f"{self.title} ({self.score} upvotes)\n{self.url}\n{content_preview}"

    def is_image_url(self, url):
        # Check if the URL ends with common image extensions
        image_extensions = ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.webp']
        return any(url.lower().endswith(ext) for ext in image_extensions)

    def fetch_post(self):
        try:
            # Skip if the URL points to an image
            if self.is_image_url(self.url):
                self.content = "Skipped image content."
                return

            response = requests.get(self.url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            # Use a regular expression to extract the post content
            # Adjust the regex pattern based on the actual structure of the HTML
            content_pattern = re.compile(r'<div class="text-neutral-content" slot="text-body">(.*?)</div>', re.DOTALL)
            match = content_pattern.search(response.text)
            
            if match:
                # Clean up the extracted content (remove HTML tags, extra spaces, etc.)
                self.content = re.sub(r'<.*?>', '', match.group(1)).strip()
            else:
                self.content = self.url
        except requests.exceptions.RequestException as e:
            self.content = f"Failed to fetch content: {e}"
    
    def _clean_content_decorator(func):
        def wrapper(self):
            content = func(self)
            # Remove extra spaces and newlines
            content = re.sub(r'\s+', ' ', content)
            # Remove leading/trailing spaces
            content = content.strip()
            return content
        return wrapper

    @_clean_content_decorator
    def read_post(self):
        return self.content