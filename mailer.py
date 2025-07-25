import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv() # Loading environment variables

def send_plain_email(receiver_email: str, subject: str, body: str ):
    try:
        sender_email = os.getenv("SENDER_MAIL")
        password = os.getenv("MAIL_PASSWORD")

        # Create email message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject

        # Attach the plain text body
        message.attach(MIMEText(body, "plain"))

        # Connect to SMTP server and send email
        with smtplib.SMTP(os.getenv("MAIL_SERVER"), os.getenv("SMTP_PORT")) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        print("Email sent successfully!")
        return True

    except Exception as e:
        print("Error sending email:", e)
        return False

