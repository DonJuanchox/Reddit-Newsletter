# Reddit Newsletter

This project automates the process of fetching top posts from specified subreddits, formats them into an HTML email, and sends the compiled newsletter to a designated recipient.

## Features

- Fetches top posts from user-defined subreddits.
- Filters posts based on a minimum score threshold.
- Extracts and cleans post content for clarity.
- Generates structured HTML content for the email.
- Sends the formatted newsletter via email.

## Prerequisites

Before running the script, ensure you have the following:

- Python 3.x installed on your system.
- A Reddit account with API credentials.
- An email account (preferably Gmail) with an application-specific password.

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/DonJuanchox/Reddit-Newsletter.git
   cd Reddit-Newsletter
   ```

2. **Set Up a Virtual Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:

   Create a `.env` file in the project root directory with the following variables:

   ```ini
   CLIENT_ID=your_reddit_client_id
   CLIENT_SECRET=your_reddit_client_secret
   USER_AGENT=your_reddit_user_agent
   REDDIT_USERNAME=your_reddit_username
   REDDIT_PASSWORD=your_reddit_password
   E_SENDER=your_email_address
   E_PSWD=your_email_app_password
   ```

   - Replace `your_reddit_client_id`, `your_reddit_client_secret`, etc., with your actual credentials.
   - To obtain Reddit API credentials, create a new application [here](https://www.reddit.com/prefs/apps).
   - For Gmail users, generate an application-specific password by following [Google's instructions](https://support.google.com/accounts/answer/185833).

## Usage

After setting up, run the script:

```bash
python reddit_newsletter.py
```

The script will fetch top posts from the specified subreddits, compile them into an HTML email, and send it to the configured recipient.

## Customization

- **Subreddits**: Modify the `subreddits` list in `reddit_newsletter.py` to include your desired subreddits.
- **Post Limit and Score Threshold**: Adjust the `limit` and `min_score` parameters in the `fetch_top_posts` function to control the number of posts fetched and the minimum score required.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your enhancements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

*Note*: Ensure that your email provider allows sending emails via SMTP and that you've configured any necessary settings to permit the script to send emails on your behalf.
