#!/usr/bin/python
#-*- coding: utf-8 -*-
import sys
import os
import string
import smtplib
from imaplib import IMAP4, IMAP4_SSL
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

reload(sys)  
sys.setdefaultencoding('utf8')

def SMTPServer(title, sender, to, content):
	server = 'mail.pegatroncorp.com'
	username = "PEGA\\bg3_ptd"
	password = "pega#1234"

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
			strMessage['To'] = ", ".join(to)#print ", ".join(to)#strMessage['To'] = to
      #strMessage['To'] = ", ".join(to) ##//multiple recipints
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
		#print("SMTP failed: \n{0}".format(e))
		raise e
    #return e.args
	
	else:
		print("SMTP send mail Success\n")
		return str(0)

'''
if __name__ == '__main__':
	SMTPServer("yichieh_chen@pegatroncorp.com","?³ä???234","?‹å?ç¾Ž~;%22-Q~@http")
'''