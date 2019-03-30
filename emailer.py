import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(to, text):
    login = "JobsForEverybody@yandex.ru"
    password = "JobsForEverybody123"
    url = "smtp.yandex.ru"

    msg = MIMEMultipart()
    msg['Subject'] = 'Вакансии с JFE'
    msg['From'] = 'JobsForEverybody@yandex.ru'
    body = text
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP_SSL(url, 465)
        server.login(login, password)
        server.sendmail(login, to, msg.as_string())
        server.quit()
    except Exception:
        pass
