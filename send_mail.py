import smtplib
import email.mime.text
import email.mime.multipart

def simply_sendmail(host, port, username, password,
                    destination, subject, text):
    smtp = smtplib.SMTP()
    smtp.connect(host, port)
    smtp.starttls()
    smtp.login(username, password)
    msg = email.mime.multipart.MIMEMultipart('alternative')
    msg['From'] = username
    msg['To'] = destination
    msg['Subject'] = subject
    msg.attach(email.mime.text.MIMEText(text.replace('\n','<br>'),
                                        'html', 'utf-8'))
    smtp.sendmail(username, destination, msg.as_string())

class mail_sender:
    def __init__(self, host, port, username, password):
        self.smtp = smtplib.SMTP()
        self.smtp.connect(host, port)
        self.smtp.starttls()
        self.smtp.login(username, password)

