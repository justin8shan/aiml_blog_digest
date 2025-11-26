"""
Email digest generator and sender module.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
from datetime import datetime
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailDigest:
    """Generates and sends email digests of blog articles."""
    
    def __init__(self, email_config: Dict, footer_config: Dict, blogs_config: Dict):
        """
        Initialize the email digest generator.
        
        Args:
            email_config: Email configuration dictionary
            footer_config: Footer configuration dictionary
            blogs_config: Blogs configuration dictionary
        """
        self.config = email_config
        self.footer_config = footer_config
        self.blogs_config = blogs_config
        self.smtp_server = email_config['email']['smtp_server']
        self.smtp_port = email_config['email']['smtp_port']
        self.recipients = email_config['email']['recipients']
        self.subject_template = email_config['email']['subject_template']
        self.use_html = email_config['email'].get('use_html', True)
        
        # Get credentials from environment variables
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        
    def generate_html_digest(self, categorized_articles: Dict[str, List],
                            week_start: str) -> str:
        """
        Generate HTML email digest.
        
        Args:
            categorized_articles: Dictionary mapping categories to article lists
            week_start: Week start date string
            
        Returns:
            HTML string
        """
        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1 {{
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #2980b9;
                    margin-top: 30px;
                    border-left: 4px solid #3498db;
                    padding-left: 10px;
                }}
                .article {{
                    margin-bottom: 25px;
                    padding: 15px;
                    background-color: #f8f9fa;
                    border-radius: 5px;
                }}
                .article-title {{
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 5px;
                }}
                .article-title a {{
                    color: #2c3e50;
                    text-decoration: none;
                }}
                .article-title a:hover {{
                    color: #3498db;
                }}
                .article-meta {{
                    color: #7f8c8d;
                    font-size: 14px;
                    margin-bottom: 10px;
                }}
                .article-summary {{
                    color: #555;
                    font-size: 15px;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    color: #7f8c8d;
                    font-size: 14px;
                    text-align: center;
                }}
                .stats {{
                    background-color: #e8f4f8;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 30px;
                }}
            </style>
        </head>
        <body>
            <h1>📊 Weekly AI/ML Blog Digest</h1>
            <div class="stats">
                <strong>Week of {week_start}</strong><br>
                Total Articles: {sum(len(articles) for articles in categorized_articles.values())}<br>
                Categories: {len([c for c in categorized_articles.keys() if categorized_articles[c]])}
            </div>
        """
        
        # Sort categories to put "Other" last
        sorted_categories = sorted(
            categorized_articles.keys(),
            key=lambda x: (x == "Other", x)
        )
        
        for category in sorted_categories:
            articles = categorized_articles[category]
            if not articles:
                continue
                
            html += f"\n            <h2>📚 {category} ({len(articles)} articles)</h2>\n"
            
            for article in articles:
                published_str = ""
                if article.published:
                    published_str = article.published.strftime("%B %d, %Y")
                
                html += f"""
            <div class="article">
                <div class="article-title">
                    <a href="{article.link}" target="_blank">{article.title}</a>
                </div>
                <div class="article-meta">
                    <strong>{article.source}</strong>{' • ' + published_str if published_str else ''}
                </div>
                <div class="article-summary">
                    {article.summary}
                </div>
            </div>
                """
        
        # Generate footer
        html += self._generate_html_footer()
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def generate_text_digest(self, categorized_articles: Dict[str, List],
                            week_start: str) -> str:
        """
        Generate plain text email digest.
        
        Args:
            categorized_articles: Dictionary mapping categories to article lists
            week_start: Week start date string
            
        Returns:
            Plain text string
        """
        text = f"Weekly AI/ML Blog Digest - Week of {week_start}\n"
        text += "=" * 60 + "\n\n"
        
        total_articles = sum(len(articles) for articles in categorized_articles.values())
        text += f"Total Articles: {total_articles}\n\n"
        
        # Sort categories to put "Other" last
        sorted_categories = sorted(
            categorized_articles.keys(),
            key=lambda x: (x == "Other", x)
        )
        
        for category in sorted_categories:
            articles = categorized_articles[category]
            if not articles:
                continue
                
            text += f"\n{category.upper()} ({len(articles)} articles)\n"
            text += "-" * 60 + "\n\n"
            
            for article in articles:
                text += f"• {article.title}\n"
                text += f"  Source: {article.source}\n"
                if article.published:
                    text += f"  Date: {article.published.strftime('%B %d, %Y')}\n"
                text += f"  Link: {article.link}\n"
                if article.summary:
                    text += f"  Summary: {article.summary}\n"
                text += "\n"
        
        # Add footer
        text += self._generate_text_footer()
        
        return text
    
    def send_digest(self, categorized_articles: Dict[str, List]) -> bool:
        """
        Send email digest to configured recipients.
        
        Args:
            categorized_articles: Dictionary mapping categories to article lists
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.sender_email or not self.email_password:
            logger.error("Email credentials not found in environment variables")
            logger.info("Please set SENDER_EMAIL and EMAIL_PASSWORD environment variables")
            return False
        
        # Calculate week start date
        week_start = datetime.now().strftime("%B %d, %Y")
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = self.sender_email
        msg['To'] = ', '.join(self.recipients)
        msg['Subject'] = self.subject_template.format(date=week_start)
        
        # Generate digest content
        text_content = self.generate_text_digest(categorized_articles, week_start)
        text_part = MIMEText(text_content, 'plain')
        msg.attach(text_part)
        
        if self.use_html:
            html_content = self.generate_html_digest(categorized_articles, week_start)
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
        
        # Send email
        try:
            logger.info(f"Connecting to SMTP server {self.smtp_server}:{self.smtp_port}...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.email_password)
                server.send_message(msg)
            
            logger.info(f"Email digest sent successfully to {', '.join(self.recipients)}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    def _generate_html_footer(self) -> str:
        """
        Generate HTML footer with author info, disclaimer, and blog sources.
        
        Returns:
            HTML string for footer
        """
        footer_info = self.footer_config['footer']
        
        html = """
            <div class="footer">
                <hr style="border: none; border-top: 2px solid #ddd; margin: 30px 0 20px 0;">
                
                <div style="margin-bottom: 20px;">
                    <h3 style="color: #2c3e50; margin-bottom: 10px;">📝 About This Digest</h3>
                    <p style="margin: 5px 0;">{}</p>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h3 style="color: #2c3e50; margin-bottom: 10px;">👤 Author</h3>
                    <p style="margin: 5px 0;"><strong>{}</strong></p>
                    <p style="margin: 5px 0;">Contact: <a href="mailto:{}">{}</a></p>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h3 style="color: #2c3e50; margin-bottom: 10px;">📚 Blog Sources</h3>
                    <p style="margin: 5px 0;">This digest aggregates content from the following sources:</p>
                    <ul style="margin-top: 10px; padding-left: 20px;">
        """.format(
            footer_info['description'].strip(),
            footer_info['author']['name'],
            footer_info['author']['email'],
            footer_info['author']['email']
        )
        
        # Add blog sources
        for blog in self.blogs_config['blogs']:
            html += f"""
                        <li style="margin: 5px 0;">
                            <a href="{blog['url']}" target="_blank" style="color: #2980b9; text-decoration: none;">
                                {blog['name']}
                            </a>
                        </li>
            """
        
        html += """
                    </ul>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h3 style="color: #2c3e50; margin-bottom: 10px;">⚖️ Disclaimer</h3>
                    <p style="margin: 5px 0; font-size: 13px; color: #666;">{}</p>
                </div>
                
                <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #ddd;">
                    <p style="font-size: 13px; color: #999; margin: 5px 0;">{}</p>
                    <p style="font-size: 13px; color: #999; margin: 5px 0;">{}</p>
                </div>
            </div>
        """.format(
            footer_info['disclaimer'].strip(),
            footer_info['contact_info'].strip(),
            footer_info['unsubscribe_note'].strip()
        )
        
        return html
    
    def _generate_text_footer(self) -> str:
        """
        Generate plain text footer with author info, disclaimer, and blog sources.
        
        Returns:
            Plain text string for footer
        """
        footer_info = self.footer_config['footer']
        
        text = "\n" + "=" * 60 + "\n"
        text += "ABOUT THIS DIGEST\n"
        text += "=" * 60 + "\n"
        text += footer_info['description'].strip() + "\n\n"
        
        text += "AUTHOR\n"
        text += "-" * 60 + "\n"
        text += f"Name: {footer_info['author']['name']}\n"
        text += f"Contact: {footer_info['author']['email']}\n\n"
        
        text += "BLOG SOURCES\n"
        text += "-" * 60 + "\n"
        text += "This digest aggregates content from:\n\n"
        for blog in self.blogs_config['blogs']:
            text += f"  • {blog['name']}\n"
            text += f"    {blog['url']}\n\n"
        
        text += "DISCLAIMER\n"
        text += "-" * 60 + "\n"
        text += footer_info['disclaimer'].strip() + "\n\n"
        
        text += "=" * 60 + "\n"
        text += footer_info['contact_info'].strip() + "\n"
        text += footer_info['unsubscribe_note'].strip() + "\n"
        
        return text
