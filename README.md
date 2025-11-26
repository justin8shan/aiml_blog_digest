# AI/ML Blog Digest 📊

Automatically generate and email weekly summaries of new articles from top Data Science & Engineering blogs from tech companies.

## Features

- 📰 **Automated Article Collection**: Fetches articles from RSS feeds of major tech company blogs
- 🏷️ **Smart Categorization**: Groups articles by subject areas (Machine Learning, NLP, Computer Vision, etc.)
- 📧 **Email Digests**: Sends beautifully formatted HTML email summaries
- ⏰ **Scheduled Execution**: Runs automatically every Monday via GitHub Actions
- ⚙️ **Configurable**: Easy-to-customize blog sources and email recipients

## Project Structure

```
aiml_blog_digest/
├── .github/
│   └── workflows/
│       └── weekly_digest.yml      # GitHub Actions workflow
├── config/
│   ├── blogs.yaml                 # List of tech blogs to monitor
│   ├── categories.yaml            # Article categorization keywords
│   ├── email_config.yaml          # Email settings and recipients
│   └── footer_config.yaml         # Email footer content
├── src/
│   ├── main.py                    # Main orchestration script
│   ├── scraper.py                 # Blog article scraper
│   ├── categorizer.py             # Article categorization logic
│   ├── email_digest.py            # Email generation and sending
│   └── utils.py                   # Configuration utilities
├── requirements.txt               # Python dependencies
├── LICENSE
└── README.md
```

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/justin8shan/aiml_blog_digest.git
cd aiml_blog_digest
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Email Recipients

Edit `config/email_config.yaml` and update the recipients list:

```yaml
email:
  recipients:
    - "your.email@example.com"  # Replace with your email
```

### 4. Set Up Email Credentials

For local testing, set environment variables:

```bash
export SENDER_EMAIL="your.email@gmail.com"
export EMAIL_PASSWORD="your-app-password"
```

**Note**: For Gmail, you'll need to:
1. Enable 2-factor authentication
2. Generate an [App Password](https://support.google.com/accounts/answer/185833)
3. Use the App Password instead of your regular password

### 5. Configure GitHub Secrets (for automated runs)

In your GitHub repository:
1. Go to Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `SENDER_EMAIL`: Your email address
   - `EMAIL_PASSWORD`: Your email app password

## Usage

### Run Locally

Generate and send digest:
```bash
cd src
python main.py
```

Generate digest without sending email (for testing):
```bash
cd src
python main.py --no-email
```

Fetch articles from the last 14 days:
```bash
cd src
python main.py --days 14
```

### Run via GitHub Actions

The workflow is configured to run automatically every Monday at 9:00 AM UTC.

You can also trigger it manually:
1. Go to Actions tab in GitHub
2. Select "Weekly Blog Digest" workflow
3. Click "Run workflow"

## Configuration

### Adding/Removing Blogs

Edit `config/blogs.yaml`:

```yaml
blogs:
  - name: "Blog Name"
    url: "https://example.com/blog"
    rss_feed: "https://example.com/feed"
```

### Customizing Categories

Edit `config/categories.yaml` to add new categories or modify keywords:

```yaml
categories:
  Your Category Name:
    keywords:
      - "keyword1"
      - "keyword2"
```

### Email Configuration

Edit `config/email_config.yaml`:

```yaml
email:
  smtp_server: "smtp.gmail.com"  # Change for different email providers
  smtp_port: 587
  recipients:
    - "email1@example.com"
    - "email2@example.com"
  subject_template: "Weekly AI/ML Blog Digest - Week of {date}"
  use_html: true
```

## Included Blog Sources

The default configuration includes articles from:
- Netflix Tech Blog
- Uber Engineering Blog
- Google AI Blog
- Meta AI Blog
- AWS Machine Learning Blog
- Microsoft AI Blog
- Airbnb Tech Blog
- LinkedIn Engineering Blog
- Spotify Engineering Blog
- Twitter Engineering Blog
- Databricks Blog
- OpenAI Blog

## Article Categories

Articles are automatically categorized into:
- Machine Learning
- Natural Language Processing
- Computer Vision
- Data Engineering
- Data Science
- AI Infrastructure
- Recommendation Systems
- Generative AI
- Other (uncategorized)

## Troubleshooting

### No articles found
- Check that RSS feeds are still valid
- Try increasing the `--days` parameter
- Verify internet connectivity

### Email not sending
- Verify `SENDER_EMAIL` and `EMAIL_PASSWORD` environment variables
- Check email provider's SMTP settings
- Ensure App Password is used (for Gmail)
- Check spam folder

### GitHub Actions failing
- Verify secrets are set correctly
- Check Actions logs for specific errors
- Ensure dependencies are correctly specified

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

See LICENSE file for details.

## Support

For issues and questions, please open an issue on GitHub.
AI/ML/DS blog summary from top tech companies
