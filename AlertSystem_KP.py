# encoding: utf-8
#!/usr/bin/python
import MySQLdb
from pegaSMTP import ( SMTPServer )
import sys
import HTML
import time

# E-MAILs
def get_email(idName):
    name = [
        "Albert1_Wu","Miko_Chen","Kristen_Lin"
    ]
    email = name[0] + "@pegatroncorp.com"     
    email = idName + "@pegatroncorp.com"
    return [email]

def get_subscribe():
    sub = [
        "Albert1_Wu","Miko_Chen","Kristen_Lin","Sean1_Hsu","Andyjy_Chen","Yichieh_Chen"
    ]
    sub = ["Albert1_Wu"]
    return sub    

# API for sending the mail
def Send_mail(title, to, sender, content, date):
    _title = title
    _to = to
    _sender = sender
    _content = ""
    fact_list = []
    for fact in content:
        fact_list.append(fact)
    fact_list = sorted(fact_list)
    for i in range(len(fact_list)):
        _content += ("<br/><font face='Calibri', font size='4'><b>&#8212 " + fact_list[i] + \
                     " &#8212<b/></font><br/>")
        _content += content[fact_list[i]]
    #_content = content
    if isinstance(_title, unicode):
        _title = _title.encode('utf-8')
    if isinstance(_to, unicode):
        _to = _to.encode('utf-8')
    if isinstance(_sender, unicode):  
        _sender = _sender.encode('utf-8')
    if isinstance(_content, unicode):
        _content = _content.encode('utf-8')    
    #///smtp 
    try:
        sentmsg = "<br/><font face='Calibri', font size='3'>" + "Sent from " + _sender + "</font><br/>"
        opening = "To Whom It May Concern:"
        opening = "<font face='Calibri', font size='3'>" + opening + "</font><br/><br/>"
        date = date[0:4] + "/" + date[4:6] + "/" + date[6:8]
        intro0 = "Date of Analysis: " + date
        intro1 = "The content of this mail is the latest results of the Key Part Analysis."
        intro2 = "They are formatted as tables with respect to corresponding factories."
        intro3 = "Only those with strong correspondence (p < 0.05) are shown in the tables."
        intro4 = "*By clicking on the colored cell can you be directed to the plots via hyper link."
        intro = "<font face='Calibri', font size='3', color='Blue'>" + intro0 + "</font><br/>" + \
                "<font face='Calibri', font size='3'>" + intro1 + "</font><br/>" + \
                "<font face='Calibri', font size='3'>" + intro2 + "</font><br/>" + \
                "<font face='Calibri', font size='3'>" + intro3 + "</font><br/>" + \
                "<font face='Calibri', font size='3'>" + intro4 + "</font><br/>"
        _content = opening + intro + _content
        smt_ret = SMTPServer(_title,"bg3_ptd@pegatroncorp.com",_to,_content + sentmsg)
        return smt_ret    
    except Exception, e:
        print("SMTP Server FAIL: \n{0}".format(e))
        return e.args

# Rearranging the input list as a dictionary with respect to factory as highest stage
def ByFactory(inList):
    kp = {}
    for each in inList:
        factory = each[0]
        kp[factory] = {}
    for each in inList:
        factory = each[0]
        keypart = each[1]
        kp[factory][keypart] = {}
    for each in inList:
        factory = each[0]
        keypart = each[1]
        station = each[2]
        ranking = each[3]
        picture = each[4]
        kp[factory][keypart][station] = []
        vendors = ranking.split("<")
        rankStr = ""
        for i in range(len(vendors)-1):            
            omitted = vendors[i].split("(")
            percent = float(omitted[1][0:5])
            percent *= 100.0
            vendorStr = omitted[0] + "(" + str(percent) + ")"
            rankStr += (vendorStr + "<br/>")
            #rankStr += (vendors[i] + "\n")
        omitted = vendors[len(vendors)-1].split("(")
        percent = float(omitted[1][0:5])
        percent *= 100.0
        vendorStr = omitted[0] + "(" + str(percent) + ")"
        rankStr += vendorStr
        #rankStr += vendors[len(vendors)-1]
        kp[factory][keypart][station].append(rankStr)
        kp[factory][keypart][station].append(picture)
    return kp

# Create the HTML Table
def HTMLtable_byFactory(inList):
    ret_dict = ByFactory(inList)
    kp_byFactory = {}
    for fact in ret_dict:
        kp_byFactory[fact] = []
        tmpFactList = []
        keypartList = []
        stationList = []        
        for kp in ret_dict[fact]:
            for station in ret_dict[fact][kp]:
                if station not in stationList:
                    stationList.append(station)
        stationList = sorted(stationList)
        kp_byFactory[fact].append(stationList)
        for kp in ret_dict[fact]:
            kpStr = []
            kpStr.append(kp)
            for station in stationList:
                if station in ret_dict[fact][kp]:
                    kpStr.append(ret_dict[fact][kp][station][0]+";"+ret_dict[fact][kp][station][1])
                else:
                    kpStr.append("")
            kp_byFactory[fact].append(kpStr)
        kp_byFactory[fact][0].insert(0, "KP/Station(%)")
    return kp_byFactory

# The function to send the mail
def KP_Alert(inList, date, send_command=True):
    html_fact = HTMLtable_byFactory(resList)
    html_dict = {}
    sendDict = {}
    for fact in html_fact:
        sendDict[fact] = []
        for i in range(len(html_fact[fact])):
            tmpArr = []
            for j in  range(len(html_fact[fact][i])):
                if i > 0 and j > 0 and html_fact[fact][i][j] != "":
                    rankStr = html_fact[fact][i][j].split(";")[0]
                    rankStr = "<font face='Calibri', font size='2'>" + rankStr + "</font>"
                    # The folder of the plots is at: http://bg3-rd.pegatroncorp.com/KP/
                    rankURL = html_fact[fact][i][j].split(";")[1]
                    rankURL = "http://bg3-rd.pegatroncorp.com/KP/" + rankURL
                    #hrefStr = "<a style='color:black' href='" + rankURL + "'>"
                    hrefStr = "<a style='color:black;text-decoration:none' href='" + rankURL + "'>"
                    #rankStr = "<a style='color:black;text-decoration:none' href='#'>" + rankStr + "</a>"
                    rankStr = hrefStr + rankStr + "</a>"
                    tmp = HTML.TableCell(rankStr, bgcolor='#FFCCFF')
                    tmpArr.append(tmp)
                else:
                    tmp = "<font face='Calibri'><b>" + html_fact[fact][i][j] + "<b/></font>"
                    tmpArr.append(tmp)                    
            sendDict[fact].append(tmpArr)
        htmlcode = HTML.table(sendDict[fact])
        html_dict[fact] = htmlcode
    
    # Get the subscription list    
    sub_list = get_subscribe()
    for ID in sub_list:        
        # Send the mail
        if send_command:
            if html_dict:
                print "*********************************************"    
                ret = Send_mail("[RMON] Daily Alert (KP Analysis)", get_email(ID), "RMON Alerting System", html_dict, date)
                if ret == "0":
                    print "Mail Sent to " + get_email(ID)[0] + " success!"
                else:
                    print "Mail Sent to " + get_email(ID)[0] + " failed!"
                    if ret[0] == 'Connection unexpectedly closed':
                        time.sleep(15)
                        ret = Send_mail("[RMON] Daily Alert (KP Analysis)", get_email(ID), "RMON Alerting System", html_dict, date)
                        while ret[0] == 'Connection unexpectedly closed':
                            ret = Send_mail("[RMON] Daily Alert (KP Analysis)", get_email(ID), "RMON Alerting System", html_dict, date)
                            time.sleep(15)
                            if ret == "0":
                                print "Mail Sent to " + get_email(ID)[0] + " success!"
                            elif ret[0] == 'Connection unexpectedly closed':
                                print "Mail Sent to " + get_email(ID)[0] + " fail due to bad connection!"
                            else:
                                raise
                time.sleep(15)
    print "*********************************************" 
    return True  
    
htmlcode_sample = """
<html>
<head>
<style type='text/css'>
a span.tooltip {display:none;}
a:hover span.tooltip {position:absolute;top:30px;left:20px;display:inline;border:2px solid green;}
</style>
</head>
<body>
<div title="1)&#009;A&#013;&#010;2)&#009;B">Hover Me</div>
<a href="lala">hover<span class="tooltip">tooltip</span></a>
<IMG SRC="http://www.mysite.com/images/monkey-image-here.gif" ALT="Picture of a cool monkey!">
</body>
</html>
"""

if __name__ == "__main__":
    # MySQL connector
    db = MySQLdb.connect(host="172.28.138.62", user="albert", passwd="pega#1234", db="Musculus")
    cursor = db.cursor()
    date = sys.argv[1]
    sql_command = "select factory, keypart, test_station, median_relation, picture_name from abnormal where date = '%s';" % (date)
    cursor.execute(sql_command)
    results = cursor.fetchall()
    db.close()
    resList = map(list, results)
    KP_Alert(resList, date, True) # The default sent command is set to be True 