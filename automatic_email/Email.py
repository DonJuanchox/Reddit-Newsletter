import os
import email
from email import policy
from email.parser import BytesParser

class Email(object):
    """
    This class models an Email to avoid dealing with the Win32 Email interface.
    """
    
    def __init__(self, raw_email):
        self._email = BytesParser(policy=policy.default).parsebytes(raw_email)

    def get_sender_name(self):
        return self._email["From"]

    def get_sender_address(self):
        return self._email["From"]

    def get_to_name(self):
        return self._email["To"]

    def get_subject(self):
        return self._email["Subject"]

    def get_body(self):
        if self._email.is_multipart():
            return self._email.get_payload(0).get_payload(decode=True).decode()
        return self._email.get_payload(decode=True).decode()

    def get_html_body(self):
        if self._email.is_multipart():
            for part in self._email.iter_parts():
                if part.get_content_type() == "text/html":
                    return part.get_payload(decode=True).decode()
        return None

    def get_timestamp(self):
        return self._email["Date"]

    def save_attachments(self, path):
        """
        Saves all the attachments from the email to the specified path.
        """
        for part in self._email.iter_parts():
            if part.get_content_disposition() == "attachment":
                filename = part.get_filename()
                if filename:
                    with open(os.path.join(path, filename), "wb") as f:
                        f.write(part.get_payload(decode=True))
    
    def get_attachments(self, temp_path):
        """
        Get byte content of attachments.
        """
        contents = []
        for part in self._email.iter_parts():
            if part.get_content_disposition() == "attachment":
                filename = os.path.join(temp_path, part.get_filename())
                with open(filename, "wb") as f:
                    f.write(part.get_payload(decode=True))
                with open(filename, "rb") as f:
                    contents.append(f.read())
        return contents
    
    def __str__(self):
        sender = self.get_sender_name()
        to = self.get_to_name()
        subj = self.get_subject()
        when = self.get_timestamp()
        return f"From: {sender}, To: {to}, Subject: {subj}, on: {when}"
