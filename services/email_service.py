# SECURITY-REVIEWED: 2026-06-24 | RULES: v2.6.0-draft
import logging
import smtplib
import random
from email.mime.text import MIMEText
from email.header import Header

import util
from settings import cfg


def generate_code():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])


def send_verification_email(to_email: str) -> bool:
    validate_code = generate_code()

    message = MIMEText(f"您好！您的验证码是：{validate_code}，5分钟内有效。", 'plain', 'utf-8')
    message['From'] = Header(cfg.EMAIL_SENDER)
    message['To'] = Header(to_email)
    message['Subject'] = Header("您的验证码", 'utf-8')

    try:
        server = smtplib.SMTP_SSL(cfg.EMAIL_SMTP_HOST, cfg.EMAIL_SMTP_PORT)
        server.login(cfg.EMAIL_SENDER, cfg.EMAIL_PASSWORD)
        server.sendmail(cfg.EMAIL_SENDER, [to_email], message.as_string())
        server.quit()
        util.save_email_token(to_email, validate_code)
        logging.info("验证码邮件发送成功！")
        return True
    except Exception as e:
        logging.error(f"邮件发送失败: {e}")
        return False