import os
import smtplib
import platform
import imaplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Try to import `win32com.client` (only works on Windows)
try:
    import win32com.client as win32
    OUTLOOK_AVAILABLE = True
except ImportError:
    OUTLOOK_AVAILABLE = False

class Email_Access:
    """
    This class sends and retrieves emails using:
    - Outlook (if sender's email is an Outlook account & system is Windows)
    - SMTP (for sending)
    - IMAP (for retrieving)
    """

    def __init__(self, smtp_server=None, smtp_port=587, smtp_username=None, smtp_password=None, imap_server=None, outlook_domains=None):
        """
        Initializes email client. Uses Outlook if sender email is from an Outlook account.
        Otherwise, it defaults to SMTP.
        """
        self.outlook_domains = outlook_domains or ["outlook.com", "hotmail.com", "live.com", "microsoft.com", "gruposantander.com"]

        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.imap_server = imap_server  # IMAP server for receiving emails

    def send_email(self, from_address, to_address, subject, body, attachment_paths=None, html_body=False, cc_address=None):
        """
        Sends an email based on the sender's email domain.
        - Uses **Outlook** if the sender's domain matches Outlook domains.
        - Uses **SMTP** for all other emails.
        """
        use_outlook = self._is_outlook_email(from_address)

        if use_outlook:
            if OUTLOOK_AVAILABLE and platform.system() == "Windows":
                self._send_email_outlook(from_address, to_address, subject, body, attachment_paths, html_body, cc_address)
            else:
                print(f"Outlook not available, falling back to SMTP for {from_address}")
                self._send_email_smtp(from_address, to_address, subject, body, attachment_paths, html_body, cc_address)
        else:
            self._send_email_smtp(from_address, to_address, subject, body, attachment_paths, html_body, cc_address)

    def fetch_emails(self, mailbox="INBOX", search_criterion="ALL", limit=10):
        """
        Fetches emails using IMAP, parses them using the Email class, and returns a list of parsed email objects.
        """
        if not self.imap_server:
            print("IMAP server not configured.")
            return []

        emails = []

        try:
            # Connect to the IMAP server
            with imaplib.IMAP4_SSL(self.imap_server) as mail:
                mail.login(self.smtp_username, self.smtp_password)
                mail.select(mailbox)

                # Search emails based on criteria (e.g., "ALL", "UNSEEN")
                status, messages = mail.search(None, search_criterion)
                if status != "OK":
                    print("No emails found.")
                    return []

                email_ids = messages[0].split()[-limit:]  # Get the latest 'limit' emails

                for e_id in email_ids:
                    status, msg_data = mail.fetch(e_id, "(RFC822)")

                    if status == "OK":
                        raw_email = msg_data[0][1]  # Extract raw email content

                        # Parse the email using Email.py
                        parsed_email = Email(raw_email)
                        emails.append(parsed_email)

        except Exception as e:
            print(f"Error fetching emails: {e}")

        return emails

    def _is_outlook_email(self, email_address):
        """
        Checks if the sender's email belongs to an Outlook-based domain.
        """
        domain = email_address.split("@")[-1].lower()
        return domain in self.outlook_domains

    def _send_email_outlook(self, from_address, to_address, subject, body, attachment_paths, html_body, cc_address):
        """
        Sends an email using Outlook.
        """
        outlook = win32.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)

        mail.SentOnBehalfOfName = from_address
        mail.To = to_address
        if cc_address:
            mail.CC = cc_address
        mail.Subject = subject

        if html_body:
            mail.HTMLBody = body
        else:
            mail.Body = body

        if attachment_paths:
            for attachment in attachment_paths:
                mail.Attachments.Add(attachment)

        mail.Send()
        print(f"Email sent successfully via Outlook as {from_address} to {to_address}")

    def _send_email_smtp(self, from_address, to_address, subject, body, attachment_paths, html_body, cc_address):
        """
        Sends an email using SMTP (Gmail, Outlook.com, etc.).
        """
        msg = MIMEMultipart()
        msg["From"] = from_address
        msg["To"] = to_address
        if cc_address:
            msg["Cc"] = cc_address
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "html" if html_body else "plain"))

        if attachment_paths:
            for attachment_path in attachment_paths:
                if os.path.exists(attachment_path):
                    with open(attachment_path, "rb") as attachment:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}")
                    msg.attach(part)

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(from_address, [to_address] + ([cc_address] if cc_address else []), msg.as_string())
            print(f"Email sent successfully via SMTP as {from_address} to {to_address}")
        except Exception as e:
            print(f"Error sending email via SMTP: {e}")
