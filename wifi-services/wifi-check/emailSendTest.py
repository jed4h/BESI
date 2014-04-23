import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import time

# get BeagleBone IP Address
import socket

sent = False

while not sent:
    try:
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.connect(("8.8.8.8", 80))
	myIP = sock.getsockname()[0]
	sent = True
    except:
	print "error"

    time.sleep(5)

msg = MIMEMultipart()
msg['From'] = 'jduganuva@gmail.com'
msg['To'] = 'jduganuva@gmail.com'
msg['Subject'] = 'simple email in python'
message = 'BeagleBone IP: {}'.format(myIP)
msg.attach(MIMEText(message))

mailserver = smtplib.SMTP('smtp.gmail.com',587)
# identify ourselves to smtp gmail client
mailserver.ehlo()
# secure our email with tls encryption
mailserver.starttls()
# re-identify ourselves as an encrypted connection
mailserver.ehlo()
mailserver.login('jduganuva@gmail.com', 'mRv4HCcza9UqgZR')

mailserver.sendmail('jduganuva@gmail.com','jduganuva@gmail.com',msg.as_string())

mailserver.quit()
