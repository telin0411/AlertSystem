# encoding: utf-8
#!/usr/bin/python
import MySQLdb
from AlertSystem import ( instant_display )
import sys
import HTML

def io_inst_disp(user_id, msg):
    htmlcode = instant_display(msg)
    fo = open("html/"+user_id+".html",'w')
    fo.write(htmlcode)
    fo.close

user_id = sys.argv[1]
msg = sys.argv[2]

io_inst_disp(user_id, msg)