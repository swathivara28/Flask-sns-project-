import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import bcrypt 



load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv('sender_email')
SENDER_PASSKEY = os.getenv('passkey')

def sendEmail(to_email: str, subject: str, body: str):
    print(SENDER_EMAIL,SENDER_PASSKEY)
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP(
            host=SMTP_SERVER,
            port=SMTP_PORT
        )
        server.starttls()
        server.login(
            user=SENDER_EMAIL,
            password=SENDER_PASSKEY
        )
        server.sendmail(
            SENDER_EMAIL,
            to_email,
            msg.as_string()
        )
        server.quit()
        return True, "Email sent to Registered Mail"
    except Exception as e:
        return False, f"Something wrong in utils.py-sendEmail(): {e}"

    

# generate hashpassword
def generateHashPassword(password:str):
    hash_password = bcrypt.hashpw(
        password=password.encode('utf-8'),
        salt=bcrypt.gensalt(4)
    )
    return hash_password

# validate hash password
def validateHashPassword(password:str, hash_password:str):
    status = bcrypt.checkpw(password = password.encode('utf-8'),
                          hashed_password=hash_password.encode('utf-8')
                          )
    return status
class EmailTemplates:

    @staticmethod
    def registerEmailTemplate(otp: int, username: str = "Dear"):
        template = f"""Hello {username},

Thanks for choosing SNS app to manage your files and notes.

Your OTP: {otp}

If you did not register for this app, please ignore this email.
Do not share your OTP with anyone.

Thank you.

Best Wishes,
SNS Management
"""
        return template

    @staticmethod
    def forgotPasswordTemplate(url: str, username: str = "User"):
        template = f"""Hello {username},

To manage your files and notes, reset your password and log in again.

Your password reset link:
{url}

If you did not request this, please ignore this email.

Thanks for choosing SNS app.

Regards,
SNS Management
"""
        return template