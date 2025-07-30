# utils.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from langchain_community.document_loaders import WebBaseLoader
import os 
from dotenv import load_dotenv
load_dotenv()
os.environ["GMAIL_USER"] = os.getenv("GMAIL_USER")
os.environ["GMAIL_PASS"] = os.getenv("GMAIL_PASS")
def send_email(recipient_email: str, subject: str, body: str) -> None:
    """Send an email dynamically using SMTP."""
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.environ("GMAIL_USER")
    sender_password = os.environ("GMAIL_PASS")

    try:
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'html'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
            print(f"Email sent successfully to {recipient_email}.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def load_blog_content(page_url: str) -> str:
    """Load content from a specific URL."""
    try:
        loader = WebBaseLoader(web_paths=[page_url], bs_get_text_kwargs={"separator": " ", "strip": True})
        loaded_content = loader.load()
        blog_content = " ".join([doc.page_content for doc in loaded_content])
        return blog_content
    except Exception as e:
        print(f"Error loading blog content from URL {page_url}: {e}")
        return ""