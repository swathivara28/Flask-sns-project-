import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import bcrypt

SMTP_SERVER="smtp.gmail.com"
SMTP_PORT=587
SENDER_EMAIL=os.getenv('sender_email')
SENDER_PASSKEY=os.getenv('passkey')

def sendEmail(to_email:str,subject:str,body:str):
    msg=MIMEMultipart()
    msg['From']=SENDER_EMAIL
    msg['To']=to_email
    msg['Subject']=subject
    msg.attach(MIMEText(body,'plain'))
    try:
        server=smtplib.SMTP(host=SMTP_SERVER,port=SMTP_PORT)
        server.starttls()
        server.login(user=SENDER_EMAIL,password=SENDER_PASSKEY)
        server.sendmail(SENDER_EMAIL,to_email,msg.as_string())
        server.quit()
        return True, "Email send to Registerd Mail"
    except Exception as e:
        return False, f"Something wrong in utils.py-sendEmail():{e}"


def generateHashPassword(password: str):
    return bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    )


def validateHashPassword(password: str, hash_password):
    return bcrypt.checkpw(
        password.encode('utf-8'),
        hash_password
    )

class EmailTemplates:
    @staticmethod
    def registerEmailTemplate(otp:int, username:str="Dear"):
        templates = f"""Hello {username},
        Thanks for chosing SNS app to  manage your files and notes
        
        Your OTP:{otp}
        
        if your not registering tothis app, simple ignore this email and don't share otp with any one.
         
        Thank you

        Best Wishes
        SNS Management"""
        return templates