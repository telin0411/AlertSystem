# encoding: utf-8
#!/usr/bin/python
import MySQLdb
from pegaSMTP import ( SMTPServer )
import sys
import HTML
import time

# E-MAILs
def get_email(name):
    address = {
        'Albert1_Wu':"Andyjy_Chen@pegatroncorp.com",
        'Miko_Chen':"Miko_Chen@pegatroncorp.com",
        'Kristen_Lin':"Kristen_Lin@pegatroncorp.com"
    }
    email = name + "@pegatroncorp.com"     
    return [email]
    #return address[name]
    
def getFile(path, section, date):
    # Read the file and do the formatting
    path = path + section + "/"
    line_days = {}
    linePath = path + "Line_days.txt"
    fline = open(linePath, 'r')
    fline.readline()
    for info in fline:
        infos = info.strip().split(",")
        lines = infos[3]
        line_days[infos[1]+","+infos[5]+","+infos[3]] = infos[0:-1]

    fact_days = {}
    factPath = path + "Factory_days.txt"
    ffact = open(factPath, 'r')
    ffact.readline()
    for info in ffact:
        infos = info.strip().split(",")
        facts = infos[2]
        fact_days[infos[1]+","+infos[5]+","+infos[2]] = infos[0:-1]
    
    Station_days = {}
    statPath = path + "Station_days.txt"
    fstat = open(statPath, 'r')
    fstat.readline()
    for info in fstat:
        infos = info.strip().split(",")
        stats = infos[2]
        Station_days[infos[1]+","+infos[5]+","+infos[3]+","+infos[4]] = infos[0:-1]    

    Sum_days = {}
    sumsPath = path + "SUM_station_days.txt"
    fsums = open(sumsPath, 'r')
    fsums.readline()
    for info in fsums:
        infos = info.strip().split(",")
        sums = infos[2]
        Sum_days[infos[1]+","+infos[5]+","+infos[4]] = infos[0:-1]    
    
    IP_days = {}
    ipPath = path + "Station_by_IP_days.txt"
    fip = open(ipPath, 'r')
    fip.readline()
    for info in fip:
        infos = info.strip().split(",")
        ip = infos[2]
        IP_days[infos[1]+","+infos[5]+","+infos[4]+","+infos[8]] = infos[0:14]  
    fline.close
    ffact.close
    fstat.close
    fsums.close
    fip.close
    return fact_days, line_days, Station_days, Sum_days, IP_days

# API for sending the mail
def Send_mail(title, to, sender, content, items):
    _title = title
    _to = to
    _sender = sender
    _content = content
    new_cont = ""
    for each in _content:
        new_cont += "<font face='Calibri', font size='3', color='Red'>" + each + "</font><br/>"
        new_cont += _content[each] + "<br/>"
    if isinstance(_title, unicode):
        _title = _title.encode('utf-8')
    if isinstance(_to, unicode):
        _to = _to.encode('utf-8')
    if isinstance(_sender, unicode):  
        _sender = _sender.encode('utf-8')
    if isinstance(_content, unicode):
        new_cont = new_cont.encode('utf-8')    
    #///smtp 
    try:
        item_str = ""
        for item in items:
            item_tmp = "* " + item
            item_tmp = "<font face='Calibri', font size='3', color='#fd6864'>" + item_tmp + "</font><br/>"
            item_str += item_tmp
        item_str += "<br/>"
        sentmsg = "<br/><font face='Calibri', font size='3'>" + "Sent from " + _sender + "</font><br/>"
        instruction = "** The colored blocks indicate your selection of filtering items"
        instruction = "<font face='Calibri', font size='3', color='Red'>" + instruction + "</font><br/><br/>"
        opening = "To Whom It May Concern:"
        opening = "<font face='Calibri', font size='3'>" + opening + "</font><br/><br/>"
        new_cont = opening + instruction + new_cont
        smt_ret = SMTPServer(_title,"bg3_ptd@pegatroncorp.com",_to,new_cont + sentmsg)
        return smt_ret    
    except Exception, e:
        print("SMTP Server FAIL: \n{0}".format(e))
        return e.args
# Function for splitting the items
def filter_split(items):
    op = ""
    if '>' in items and '=' not in items:
        op = ">"
    elif '<' in items and '=' not in items:
        op = "<"
    elif '=' in items and ('>' not in items and '<' not in items):
        op = "="
    elif '<=' in items:
        op = "<="
    elif '>=' in items:
        op = ">="
    itemList = items.split(op)
    outList = []
    outList.append(itemList[0].strip())
    outList.append(op)
    outList.append(itemList[1].strip())   
    return outList

# Function for item filterings
def Filters(items, account):
    itemDict = {
        'input':8,'fail':9,'yield':10,'retest':11,'retest(%)':12,
        'retest_abnormal':13,'retest_abnormal(%)':14,'truefail':15,'processissue':16,
        'retest_over_halfhour':17,'retest_over_halfhour(%)':18,'overstayingtime':19,
        'not_goto_fa_afterfinalfail':20,'not_goto_fa_afterfinalfail(%)':21,
        'no_qt0_afterrepair':22,'no_qt0_afterrepair(%)':23    
    }
    itemList = filter_split(items)
    item = itemList[0].lower()
    op = itemList[1]
    value = float(itemList[2])
    ret_list = []
    if op == '>':
        for each_list in account:
            if float(each_list[itemDict[item]]) > value:
                ret_list.append(each_list)
    elif op == '<':
        for each_list in account:
            if float(each_list[itemDict[item]]) < value:
                ret_list.append(each_list)                
    elif op == '>=':
        for each_list in account:
            if float(each_list[itemDict[item]]) >= value:
                ret_list.append(each_list)    
    elif op == '<=':
        for each_list in account:
            if float(each_list[itemDict[item]]) <= value:
                ret_list.append(each_list)   
    else:
        for each_list in account:
            if float(each_list[itemDict[item]]) == value:
                ret_list.append(each_list)                        
    return ret_list
    
def colored(inList, items):
    Items = {
        'input':8,'fail':9,'yield':10,'retest':11,'retest(%)':12,
        'retest_abnormal':13,'retest_abnormal(%)':14,'truefail':15,'processissue':16,
        'retest_over_halfhour':17,'retest_over_halfhour(%)':18,'overstayingtime':19,
        'not_goto_fa_afterfinalfail':20,'not_goto_fa_afterfinalfail(%)':21,
        'no_qt0_afterrepair':22,'no_qt0_afterrepair(%)':23    
    }
    outList = []
    for each_item in items:
        tmp = []
        for each_list in inList:
            each_list[Items[each_item]] = HTML.TableCell(each_list[Items[each_item]], bgcolor='#fd6864',
                                                         attribs={'style': 'font-family: Calibri'})
    return inList

def formatting(inList, filters, Header):
    defaultItem = {'input':8, 'fail':9, 'yield':10, 'retest':11}
    extrasItem = {
        'retest_abnormal':13,'retest_abnormal(%)':14,'truefail':15,'processissue':16,
        'retest_over_halfhour':17,'retest_over_halfhour(%)':18,'overstayingtime':19,
        'not_goto_fa_afterfinalfail':20,'not_goto_fa_afterfinalfail(%)':21,
        'no_qt0_afterrepair':22,'no_qt0_afterrepair(%)':23    
    }
    outList = []
    out_index = []
    out_header = []
    for each_filter in filters:
        if each_filter in extrasItem:
            out_index.append(extrasItem[each_filter])
    out_index.sort()
    out_header += Header[0:13]
    for index in out_index:
        out_header.append(Header[index])
    if len(out_index) > 0:
        for each_list in inList:
            list_tmp = []
            list_tmp.append(each_list[0:13])
            for index in out_index:
                if index <= len(each_list):
                    list_tmp[0].append(each_list[index])
            outList += (list_tmp)
    else:
        for each_list in inList:
            outList.append(each_list[0:13])
    section_dict = {"CG":[], "HSG":[], "FATP":[]}
    for each_list in outList:
        section_dict[each_list[5]].append(each_list)
    outList = []
    for keys in section_dict:
        outList += section_dict[keys]
    return outList, out_header

"""" Main Function """
def Query(resList, path, date, send_command):
    # Account Settings
    html_id = {}    
    account = {}
    for row in resList:
        User_ID = row[1]
        if User_ID not in account:
            account[User_ID] = []
    for row in resList:
        acc_detail = {}
        acc_detail["SID"] = row[0]
        acc_detail["User_ID"] = row[1]
        acc_detail["EN_Flag"] = row[2]
        acc_detail["CreateTime"] = row[3]
        acc_detail["Project"] = row[4]
        acc_detail["Section"] = row[5]
        acc_detail["Factory"] = row[6]
        acc_detail["Line"] = row[7]
        acc_detail["Station"] = row[8]
        acc_detail["Item"] = row[9]
        account[row[1]].append(acc_detail)
        
    # Processing
    answer_id = {}
    for ID in account:
        Header = [
            "Time","Project","Factory","Line","Station","Section","Stage","AE","Input",
            "Fail","Yield","Retest","Retest(%)","Retest_Abnormal","Retest_Abnormal(%)",
            "TrueFail","ProcessIssue","Retest_Over_HalfHour","Retest_Over_HalfHour(%)",
            "OverStayingTime","Not_Goto_FA_AfterFinalFail","Not_Goto_FA_AfterFinalFail(%)",
            "No_QT0_AfterRepair","No_QT0_AfterRepair(%)"
        ]    
        filters_id = []
        answer_id[ID] = {}
        filter_str = []
        for each_attr in account[ID]:
            attr_str = ""          
            answer_tmp = []
            # The answer that should be recorded in this round
            en_flag = each_attr["EN_Flag"]
            en = None
            if en_flag == '1':
                en = True
            else:
                en = False
            proj = each_attr["Project"]
            sect = each_attr["Section"]
            sid = each_attr["SID"]
            if each_attr["Factory"] != None:
                facts = each_attr["Factory"].split(";")[0:-1]
                attr_str += each_attr["Factory"] + " "
            if each_attr["Line"] != None:
                lines = each_attr["Line"].split(";")[0:-1]
                attr_str += each_attr["Line"] + " "
            if each_attr["Station"] != None:
                stats = each_attr["Station"].split(";")[0:-1]
                attr_str += each_attr["Station"] + " "
            if each_attr["Item"] != None:
                items = each_attr["Item"].split(";")[0:-1]
                attr_str += each_attr["Item"]
            # Get the file
            fact_days, line_days, Station_days, Sum_days, IP_days = getFile(path, sect, date)
            # Factory_days
            if each_attr["Factory"] != '' and each_attr["Factory"] != None:
                for each_fact in facts:
                    if '%' not in each_fact:
                        if proj+","+sect+","+each_fact in fact_days and en:
                            answer_tmp.append(fact_days[proj+","+sect+","+each_fact])
                    else:
                        for allLine in fact_days:
                            answer_tmp.append(fact_days[allLine])
        
            # Line_Station_days
            if each_attr["Line"] != '' and each_attr["Line"] != None:
                for each_line in lines:
                    line_stat = each_line.split(",")
                    if len(line_stat) <= 1: # No Stations specified under a Line
                        if '%' not in each_line:
                            if proj+","+sect+","+each_line in line_days and en:
                                answer_tmp.append(line_days[proj+","+sect+","+each_line])
                        else:
                            for allLine in line_days:
                                if allLine.split(",")[2][0:2] == each_line[0:2]:
                                    if allLine in line_days and en:
                                        answer_tmp.append(line_days[allLine]) 
                    else: # A Station has been specified under a Line
                        qLine = line_stat[0]
                        qStat = line_stat[1]
                        if '%' not in qLine and qStat != "All":
                            if proj+","+sect+","+qLine+","+qStat in Station_days and en:
                                answer_tmp.append(Station_days[proj+","+sect+","+qLine+","+qStat][0:24])
                        elif qStat == "All":
                            for allLine in Station_days:
                                if allLine.split(",")[2] == qLine:
                                    if allLine in Station_days and en:
                                        answer_tmp.append(Station_days[allLine])
                        else:
                            for allLine in Station_days:
                                if allLine.split(",")[2][0:2] == qLine[0:2] and allLine.split(",")[3] == qStat:
                                    if allLine in Station_days and en:
                                        answer_tmp.append(Station_days[allLine])
                        
            # Sum_Stations
            if each_attr["Station"] != '' and each_attr["Station"] != None:
                for each_stat in stats:
                    stat_ip = each_stat.split(",")
                    if len(stat_ip) <= 1: # No Stations specified under a Line
                        if '%' not in each_stat:
                            if proj+","+sect+","+each_stat in Sum_days and en:
                                answer_tmp.append(Sum_days[proj+","+sect+","+each_stat])
                        else:
                            for allStat in Sum_days:
                                if allStat.split(",")[2][0:2] == each_stat[0:2]:
                                    if allStat in Sum_days and en:
                                        answer_tmp.append(Sum_days[allStat]) 
                    else: # An IP has been specified under a Station
                        #print stat_ip
                        qStat = stat_ip[0]
                        qIP = stat_ip[1]
                        if '%' not in qStat and qIP != "All":
                            if proj+","+sect+","+qStat+","+qIP in IP_days and en:
                                ip_now = IP_days[proj+","+sect+","+qStat+","+qIP].pop(8)
                                IP_days[proj+","+sect+","+qStat+","+qIP][4] += ("]" + ip_now)
                                answer_tmp.append(IP_days[proj+","+sect+","+qStat+","+qIP][0:14])
                        elif qIP == "All":
                            for allStat in IP_days:
                                if allStat.split(",")[2] == qStat:
                                    if allStat in IP_days and en:
                                        ip_now = IP_days[allStat].pop(8)
                                        IP_days[allStat][4] += ("]" + ip_now)
                                        answer_tmp.append(IP_days[allStat])                             
                        else:
                            for allStat in IP_days:
                                if allStat.split(",")[2][0:2] == qStat[0:2] and allStat.split(",")[3] == qIP:
                                    if allStat in IP_days and en:
                                        ip_now = IP_days[allStat].pop(8)
                                        IP_days[allStat][4] += ("]" + ip_now)
                                        answer_tmp.append(IP_days[allStat])
            
            # Conditions
            filter_tmp = []
            filters = []
            if (each_attr["Item"] != None and each_attr["Item"] != '') and en:            
                for each_item in items:
                    filters = filter_split(each_item)
                    #print filters, ID
                    if filters[0].lower() not in filter_tmp:
                        filter_tmp.append(filters[0].lower())
                    if filters[0].lower() not in filters_id:
                        filters_id.append(filters[0].lower())
                    answer_tmp = Filters(each_item, answer_tmp)
                    filter_str.append(each_item)
            
            # Colored Highlight
            if len(filter_tmp) > 0:
                answer_tmp = colored(answer_tmp, filter_tmp)
            if answer_tmp:
                answer_id[ID][attr_str] = answer_tmp

        # Procedute to convert the results from list of lists to HTML table
        htmlcode = {}
        for each in answer_id[ID]:
            answer_id[ID][each], header = formatting(answer_id[ID][each], filters_id, Header)
            colored_header = []
            for each_ind in header:
                header_tmp = "<font face='Calibri'>" + "<b>" + each_ind + "</b>" + "</font>"
                header_tmp = HTML.TableCell(header_tmp, bgcolor='#BFA4E1')
                colored_header.append(header_tmp)
            out = []
            for each_line in answer_id[ID][each]:
                tmp = []
                for each_element in each_line:
                    if type(each_element) == str:
                        ele_tmp = "<font face='Calibri'>" + each_element + "</font>"
                    else: 
                        ele_tmp = each_element
                    tmp.append(ele_tmp)
                out.append(tmp)
            htmlcode[each] = HTML.table(out, header_row = colored_header)
        # Send the mail
        if send_command:
            if htmlcode:
                print "*********************************************"    
                ret = Send_mail("[RMON] Daily Alert", get_email(ID), "RMON Alerting System", htmlcode, filter_str)
                if ret == "0":
                    print "Mail Sent to " + get_email(ID)[0] + " success!"
                else:
                    print "Mail Sent to " + get_email(ID)[0] + " failed!"
                    if ret[0] == 'Connection unexpectedly closed':
                        time.sleep(10)
                        ret = Send_mail("[RMON] Daily Alert", get_email(ID), "RMON Alerting System", htmlcode, filter_str)
                        while ret[0] == 'Connection unexpectedly closed':
                            ret = Send_mail("[RMON] Daily Alert", get_email(ID), "RMON Alerting System", htmlcode, filter_str)
                            time.sleep(10)
                            if ret == "0":
                                print "Mail Sent to " + get_email(ID)[0] + " success!"
                            elif ret[0] == 'Connection unexpectedly closed':
                                print "Mail Sent to " + get_email(ID)[0] + " fail due to bad connection!"
                            else:
                                raise
                time.sleep(15) 
        html_id[ID] = {}
        html_id[ID] = htmlcode
    return html_id
"""" Main Function Ends Here """

def instant_display(resList):
    path = "AlertSystem/Panda/20141104/"
    date = "20141104_0400_1400"
    info = resList.split("#")
    return_dict = Query([info], path, date, False)
    return return_dict

if __name__ == "__main__":

    # MySQL connector
    #db = MySQLdb.connect("localhost","root","W1nNas171","rmon_daily")
    db = MySQLdb.connect(host="172.28.138.62", user="albert", passwd="pega#1234", db="rmon_daily")
    cursor = db.cursor()
    sql = "select * from rmon_daily.Alert_CFG;"
    cursor.execute(sql)
    results = cursor.fetchall()
    db.close()
    resList = map(list, results)

    # Execution of the main function code
    htmlcode_ALL = Query(resList, sys.argv[1], sys.argv[2], True)
    print "*********************************************"
    print "End of Today's Mail Sending Task"
    #newlist = "12#Kristen_Lin#1#20141217091220#Panda#FATP##3F04,ALS CAL(COSMETIC TRAY);#ALSAR,375365;#"
    #single_code = instant_display(newlist)
    #print single_code
    #print htmlcode_ALL["Albert1_Wu"]