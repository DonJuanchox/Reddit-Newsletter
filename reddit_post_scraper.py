"""
This module provides a `RedditPost` class for retrieving and processing Reddit post content.

The class is designed to:
- Store and represent key details of a Reddit post, such as its title, score, and URL.
- Fetch the post's content from the given URL, while handling potential request failures.
- Identify and handle image URLs separately to avoid fetching unnecessary content.
- Provide a readable string representation of a Reddit post.
- Clean and return the post content in a structured format.

Example Usage:
    >>> post = RedditPost("Example Post", 123, "https://example.com")
    >>> post.fetch_post()
    >>> print(post.read_post())

This module is particularly useful for applications that need to extract and process Reddit post content dynamically.
"""
import requests
import re
import mimetypes
import logging

class RedditPost:
    """
    A class representing a Reddit post.

    Attributes:
        title (str): The title of the post.
        score (int): The score (upvotes) of the post.
        url (str): The URL of the post.
        content (str | None): The fetched content of the post.
    """

    def __init__(self, title: str, score: int, url: str) -> None:
        """
        Initializes a RedditPost object with a title, score, and URL.

        Args:
            title (str): The title of the Reddit post.
            score (int): The score (upvotes) of the post.
            url (str): The URL of the post.
        """
        self.title: str = title
        self.score: int = score
        self.url: str = url
        self.content: str | None = None

    def __str__(self) -> str:
        """
        Returns a formatted string representation of the RedditPost object.

        Returns:
            str: A string containing the title, score, URL, and a content preview.
        """
        content_preview: str = self.content[:100] + "..." if self.content else "No content fetched"
        return f"{self.title} ({self.score} upvotes)\n{self.url}\n{content_preview}"

    @staticmethod
    def is_image_url(url: str) -> bool:
        """
        Checks if a given URL is an image by determining its MIME type.

        Args:
            url (str): The URL to check.

        Returns:
            bool: True if the URL is an image, False otherwise.
        """
        guessed_type, _ = mimetypes.guess_type(url)
        return bool(guessed_type and guessed_type.startswith("image"))

    def fetch_post(self) -> None:
        """
        Fetches the content of the Reddit post from its URL.

        - If the URL is an image, content is marked as "Skipped image content."
        - If the request fails, logs the error and stores it in `self.content`.

        Raises:
            requests.exceptions.RequestException: If the request encounters an error.
        """
        try:
            if self.is_image_url(self.url):
                self.content = "Skipped image content."
                return

            response: requests.Response = requests.get(self.url, timeout=10)
            response.raise_for_status()

            content_match: re.Match | None = re.search(
                r'<div class="text-neutral-content" slot="text-body">(.*?)</div>',
                response.text, re.DOTALL
            )
            self.content = re.sub(r'<.*?>', '', content_match.group(1)).strip() if content_match else self.url

        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch content: {e}")
            self.content = f"Failed to fetch content: {e}"

    def read_post(self) -> str:
        """
        Cleans and returns the post content.

        - Removes excessive whitespace.
        - If no content is available, returns "No content available."

        Returns:
            str: The cleaned content of the post.
        """
        return re.sub(r'\s+', ' ', self.content.strip()) if self.content else "No content available"
