# -*- coding: utf-8 -*-
import smtplib
from email.MIMEText import MIMEText
import urllib2
import re
import requests
from pytz import timezone
import str_formater


def textToSMS(text):
    
    res = []

    for letter in text:
      if letter in ['a', 'ą']:
        res.append(2)
        res.append('')
      if letter in ['b']:
        res.append(2)
        res.append(2)
        res.append('')
      if letter in ['c', 'ć']:
        res.append(2)
        res.append(2)
        res.append(2)
        res.append('')
      if letter in ['d']:
        res.append(3)
        res.append('')
      if letter in ['e', 'ę']:
        res.append(3)
        res.append(3)
        res.append('')
      if letter in ['f']:
        res.append(3)
        res.append(3)
        res.append(3)
        res.append('')
      if letter in ['g']:
        res.append(4)
      if letter in ['h']:
        res.append(4)
        res.append(4)
        res.append('')
      if letter in ['i']:
        res.append(4)
        res.append(4)
        res.append(4)
        res.append('')
      if letter in ['j']:
        res.append(5)
        res.append('')
      if letter in ['k']:
        res.append(5)
        res.append(5)
        res.append('')
      if letter in ['l', 'ł']:
        res.append(5)
        res.append(5)
        res.append(5)
        res.append('')
      if letter in ['m']:
        res.append(6)
        res.append('')
      if letter in ['n', 'ń']:
        res.append(6)
        res.append(6)
        res.append('')
      if letter in ['o', 'ó']:
        res.append(6)
        res.append(6)
        res.append(6)
        res.append('')
      if letter in ['p']:
        res.append(7)
        res.append('')
      if letter in ['q']:
        res.append(7)
        res.append(7)
        res.append('')
      if letter in ['r']:
        res.append(7)
        res.append(7)
        res.append(7)
        res.append('')
      if letter in ['s', 'ś']:
        res.append(7)
        res.append(7)
        res.append(7)
        res.append(7)
        res.append('')
      if letter in ['t']:
        res.append(8)
        res.append('')
      if letter in ['u']:
        res.append(8)
        res.append(8)
        res.append('')
      if letter in ['v']:
        res.append(8)
        res.append(8)
        res.append(8)
        res.append('')
      if letter in ['w']:
        res.append(9)
        res.append('')
      if letter in ['x']:
        res.append(9)
        res.append(9)
        res.append('')
      if letter in ['y']:
        res.append(9)
        res.append(9)
        res.append(9)
        res.append('')
      if letter in ['z', 'ź', 'ż']:
        res.append(9)
        res.append(9)
        res.append(9)
        res.append(9)
        res.append('')
      if letter in [' ']:
        res.append(0)
        res.append('')
      if letter in ['.']:
        res.append(1)
        res.append('')
      if letter in [',']:
        res.append(1)
        res.append(1)
        res.append('')
      if letter in ['-']:
        res.append(1)
        res.append(1)
        res.append(1)
        res.append('')
    
    
    return res


def getNumbers(text):
    words = text.split()
    res = []
    for word in words:
      try:
        i = int(word)
        res.append(i)
      except:
        if word   in ['zero']:
          res.append(0)
        elif word in ['jeden', 'raz', 'pierwszy', 'pierwsza', 'pierwsze', 'pierwszą', 'pierwszego', 'pierwszemu', 'pierwszej']:
          res.append(1)
        elif word in ['dwa', 'drugi', 'druga', 'drugie', 'drugą', 'drugiego', 'drugiemu', 'drugiej']:
          res.append(2)
        elif word in ['trzy', 'trzeci', 'trzecia', 'trzecie', 'trzecią', 'trzeciego', 'trzeciemu', 'trzeciej']:
          res.append(3)
        elif word in ['cztery', 'czwarty', 'czwarta', 'czwarte', 'czwartą', 'czwartego', 'czwartemu', 'czwartej']:
          res.append(4)
        elif word in ['pięć', 'piąty', 'piąta', 'piąte', 'piątą', 'piątego', 'piątemu', 'piątej']:
          res.append(5)
        elif word in ['sześć', 'szósty', 'szósta', 'szóste', 'szóstą', 'szóstego', 'szóstemu', 'szóstej']:
          res.append(6)
        elif word in ['siedem', 'siódmy', 'siódma', 'siódme', 'siódmą', 'siódmego', 'siódmemu', 'siódmej']:
          res.append(7)
        elif word in ['osiem', 'ósmy', 'ósma', 'ósme', 'ósmą', 'ósmego', 'ósmemu', 'ósmej']:
          res.append(8)
        elif word in ['dziewięć', 'dziewiąty', 'dziewiąta', 'dziewiąte', 'dziewiątą', 'dziewiątego', 'dziewiątemu', 'dziewiątej']:
          res.append(9)
        elif word in ['dziesięć', 'dziesiąty']:
          res.append(10)
    return res

def upperUTF8(text):
    return text.upper().replace('ą','Ą').replace('ę','Ę').replace('ć','Ć').replace('ł','Ł').replace('ń','Ń').replace('ó','Ó').replace('ź','Ź').replace('ż','Ż')

def lowerUTF8(text):
    return text.lower().replace('Ą','ą').replace('Ę','ę').replace('Ć','ć').replace('Ł','ł').replace('Ń','ń').replace('Ó','ó').replace('Ź','ź').replace('Ż','ż')

def sendEmail(SUBJECT, BODY, TO, FROM, SENDER, PASSWORD, SMTP_SERVER, logger):
    """Sends an HTML email."""
    for body_charset in 'US-ASCII', 'ISO-8859-1', 'UTF-8':
        try:
            BODY.encode(body_charset)
        except UnicodeError:
            pass
        else:
            break
    msg = MIMEText(BODY.encode(body_charset), 'html', body_charset)
    msg['From'] = SENDER
    msg['To'] = TO
    msg['Subject'] = SUBJECT

    SMTP_PORT = 587
    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    session.starttls()
    session.login(FROM, PASSWORD)
    session.sendmail(SENDER, TO, msg.as_string())
    session.quit()


def emailUser(profile, logger, SUBJECT="", BODY=""):
    """
        Sends an email.

        Arguments:
        profile -- contains information related to the user (e.g., email address)
        SUBJECT -- subject line of the email
        BODY -- body text of the email
    """
    def generateSMSEmail(profile):
        """Generates an email from a user's phone number based on their carrier."""
        if profile['carrier'] is None or not profile['phone_number']:
            return None

        return str(profile['phone_number']) + "@" + profile['carrier']

    if profile['prefers_email'] and profile['gmail_address']:
        # add footer
        if BODY:
            B  = profile['first_name'] 
            B += ",<br><br>Oto twoje wiadomości:" 
            B += str_formater.unicodeToUTF8(BODY, logger)
            B += "<br>Wysłane przez osobistego asystenta"
            BODY = B

        recipient = profile['gmail_address']
        if profile['first_name'] and profile['last_name']:
            recipient = profile['first_name'] + " " + \
                profile['last_name'] + " <%s>" % recipient
    else:
        recipient = generateSMSEmail(profile)

    if not recipient:
        return False

    try:
        if 'mailgun' in profile:
            user = profile['mailgun']['username']
            password = profile['mailgun']['password']
            server = 'smtp.mailgun.org'
        else:
            user = profile['gmail_address']
            password = profile['gmail_password']
            server = 'smtp.gmail.com'
        sendEmail(SUBJECT, BODY, recipient, user,
                  "Jasper <jasper>", password, server, logger)

        return True
    except:
        return False


def getTimezone(profile):
    """
        Returns the pytz timezone for a given profile.

        Arguments:
        profile -- contains information related to the user (e.g., email address)
    """
    try:
        return timezone(profile['timezone'])
    except:
        return None


def generateTinyURL(URL):
    """
        Generates a compressed URL.

        Arguments:
        URL -- the original URL to-be compressed
    """
    target = "http://tinyurl.com/api-create.php?url=" + URL
    response = urllib2.urlopen(target)
    return response.read()


def isNegative(phrase):
    """
        Returns True if the input phrase has a negative sentiment.

        Arguments:
        phrase -- the input phrase to-be evaluated
    """
    return bool(re.search(r'\b(nie|stop|koniec|odmowa|odmawiam)\b', phrase, re.IGNORECASE))


def isPositive(phrase):
    """
        Returns True if the input phrase has a positive sentiment.

        Arguments:
        phrase -- the input phrase to-be evaluated
    """
    return bool(re.search(r'\b(tak|jasne|oczywiście|chętnie|dobrze|goł)\b', phrase, re.IGNORECASE))
