import os
import yagmail
from datetime import datetime

def send_email(content):
    if not content:
        print("近兩日無新公布處置股，不寄送郵件。")
        return
    user = os.getenv('GMAIL_USER')
    password = os.getenv('GMAIL_PASSWORD')
    target = os.getenv('RECEIVER_EMAIL').split(';')
    subject = f"【台股警訊】新進處置/注意股彙整 ({datetime.now().strftime('%Y/%m/%d')})"
    try:
        yag = yagmail.SMTP(user, password)
        yag.send(to=target, subject=subject, contents=content)
        print("Email 寄送成功！")
    except Exception as e:
        print(f"Email 寄送失敗: {e}")
