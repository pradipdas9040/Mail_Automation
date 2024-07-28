# https://www.google.com/settings/security/lesssecureapps
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
import datetime
import logging
import logging.handlers
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_file_handler = logging.handlers.RotatingFileHandler(
    "mail.log",
    maxBytes=1024 * 1024,
    backupCount=1,
    encoding="utf8",
)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
logger_file_handler.setFormatter(formatter)
logger.addHandler(logger_file_handler)

today = datetime.date.today()
formatted_date = today.strftime('%d-%m')

date_dict = {
    '10-02' : {
        'name' : 'Dhananjay',
        'email' : 'dhananjaymath7@gmail.com',
        'emogi' : '🥳'
    },
    '13-06' : {
        'name' : 'Diptiman Da',
        'email' : 'diptiman8777@gmail.com',
        'emogi' : '🍻'
    }
}

def send_mail(name, send_from, send_to, subject, message, server, port, username, password, message_type='plain', use_tls=True):
    try:
      msg = MIMEMultipart()
      msg['From'] = 'প্রদীপ (Pradip)'
      msg['To'] = name
      msg['Date'] = formatdate(localtime=True)
      msg['Subject'] = subject
      msg.attach(MIMEText(message, message_type))
      smtp = smtplib.SMTP(server, port)
      if use_tls:
          smtp.starttls()
      smtp.login(username, password)
      smtp.sendmail(send_from, send_to, msg.as_string())
      logger.info(f"Email successfully sent to {name}")
    except Exception as e:
      logger.error(e)
    finally:
      smtp.quit()

try:
  formatted_date in date_dict.keys()
  try:
    SOME_SECRET = os.environ["SOME_SECRET"]
  except:
    logger.error('Token not available!')
  info_email_subject = f"Happy Birthday {date_dict[formatted_date]['emogi']}"
  name = date_dict[formatted_date]['name']
  info_email_body = f"Hiiii {name},\nHere's to another incredible year of life! Wishing you a birthday that's as awesome as you are...😊\n"
  send_from = 'das.pra9040@gmail.com'
  send_to = date_dict[formatted_date]['email']
  Server = 'smtp.gmail.com'
  Port = 587
  sender_email_id_password = str(SOME_SECRET) 
  send_mail(name, send_from, send_to, subject=info_email_subject, message=info_email_body, server=Server, port=Port, username=send_from, password=sender_email_id_password, message_type='plain', use_tls=True)
except:
  logger.info('No birthday today')