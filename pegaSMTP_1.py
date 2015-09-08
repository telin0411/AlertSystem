#!/usr/bin/python
#-*- coding: utf-8 -*-
#######################
# 20141212 modify SMTPServer(title, sender, to, content) to SMTPServer(title, to, content)
# $sender integrater to function
#######################
import sys
import os
import string
import smtplib
import time
from imaplib import IMAP4, IMAP4_SSL
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

reload(sys)  
sys.setdefaultencoding('utf8')

def SMTPServer(title, to, content):
	server = 'mail.pegatroncorp.com'
	username = "PEGA\\bg3_ptd"
	password = "pega#1234"
	sender = "bg3_ptd@pegatroncorp.com"

	try:
		#//might need to switch to STARTTLS authentication.
		smt = smtplib.SMTP(server,587)
		smt.set_debuglevel(0)
		smt.ehlo()
		smt.starttls()
		smt.ehlo
		#//loging
		smt.login(username,password)

		try:
			#//Mail_content
			strMessage = MIMEMultipart()
			strMessage['Subject'] = title
			strMessage['From'] = sender
			#strMessage['To'] = to
			strMessage['To'] = ", ".join(to) ##//multiple recipints
			strMessage.attach(MIMEText(content, 'html'))
		
		except Exception, e:
			print("strMessage failed: \n{0}".format(e))
			return e.args

		#//mail content
		smt.sendmail(sender,to,strMessage.as_string())
		smt.close()

	except smtplib.SMTPException, e:
		print("smtplib.SMTPException failed: \n{0}".format(e))
		return e.args
	
	except Exception, e:
		print("SMTP failed: \n{0}".format(e))
		return e.args
	
	else:
		print("SMTP send mail Success\n")
		return str(0)


if __name__ == '__main__':
	for x in xrange(0,7):
		SMTPServer("?³ä???234",["yichieh_chen@pegatroncorp.com"],"?‹å?ç¾Ž~;%22-Q~@http")
		time.sleep(8)
