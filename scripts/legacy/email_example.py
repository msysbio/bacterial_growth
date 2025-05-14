import yagmail

def send_gmail():
    sender_email = "<sender>@gmail.com"
    recipient_email = "<sender>@gmail.com"
    subject = "Hello from Yagmail!"
    message = "This is an email sent using Yagmail."

    yag = yagmail.SMTP(sender_email, "") # password to be added
    yag.send(to=recipient_email, subject=subject, contents=message)
    print("Email sent using Yagmail!")

send_gmail()

import smtplib
# set up the SMTP server
s = smtplib.SMTP(host='smtp-mail.outlook.com', port=587)
s.starttls()
s.login('<subject>@student.kuleuven.be', '<password>')
