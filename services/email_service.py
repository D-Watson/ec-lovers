import logging
import smtplib
import random
from email.mime.text import MIMEText
from email.header import Header


# 1. 生成6位随机验证码
import util


def generate_code():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])


# 2. 发送邮件
def send_verification_email(to_email: str) -> bool:
    validate_code = generate_code()
    # 发件人邮箱 & 授权码（不是登录密码！）
    sender_email = "3833340167@qq.com"
    sender_password = "fozjzfutbeddcgfc"  # 在QQ邮箱设置中开启SMTP并获取授权码

    # 邮件内容
    subject = "您的验证码"
    body = f"您好！您的验证码是：{validate_code}，5分钟内有效。"

    # 构造邮件
    message = MIMEText(body, 'plain', 'utf-8')
    message['From'] = Header(sender_email)
    message['To'] = Header(to_email)
    message['Subject'] = Header(subject, 'utf-8')

    try:
        # 连接QQ邮箱SMTP服务器
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [to_email], message.as_string())
        server.quit()
        # 保存验证码到redis
        util.save_email_token(to_email, validate_code)
        logging.info("验证码邮件发送成功！")
        return True
    except Exception as e:
        logging.error(f"邮件发送失败: {e}")
        return False


# 使用示例
if __name__ == "__main__":
    to = "zhuanglinlin0321@gmail.com"  # 收件人邮箱
    send_verification_email(to)
