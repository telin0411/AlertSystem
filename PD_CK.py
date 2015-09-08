#encoding=utf8
#-*- coding: utf8 -*-
#!/usr/bin/python
#----------------------------------------------------------------------------
# Name:         PD_CK.py
# Purpose:      compare the diff with PANTHER BM
# Author:       Yichieh_chen
# Version:      1.00e(1204) support p2
# Created:      2014.11.10
# Licence:      Pegartoncorp Inc. license
#----------------------------------------------------------------------------
import sys, string, os, time, re, logging, csv, codecs, shutil
import openpyxl
from openpyxl import Workbook
import HTML
from datetime import datetime
from TraceCalls import TraceCalls
from CONFIG.config import ( BUILD, FILE_NAME, FILE_NAME_OLD, SOURCE, SKU_SOURCE, CONFIGS_LIST)
from CONFIG.pegaSMTP import ( SMTPServer )

'''
solve:UnicodeDecodeError: 'ascii' codec can't decode byte 0x?? in position 1: ordinal not in range(128)
'''
reload(sys)  
sys.setdefaultencoding('utf8')

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("PD_CK ")

TITLE_list = ['ITEM','COMPONENT','APPLE PN','PPN','DESCRIPTION','CONFIG','VENDOR','SKU']
COMPARE_OUT = 'COMPARE_OUT.html' 
t = time.time()
date = datetime.fromtimestamp(t).strftime('%Y%m%d_%H%M%S')
#date = datetime.strftime(datetime.now(), '%Y%m%d')

def log_message(msg):
    
    log.info(msg)

def display_list(lists, strs):
    for x in xrange(0,len(lists)):
        print '{0}= {1}'.format(strs, lists[x])

def _create_sku_list(files_sku='PANTHER_SKU.csv'):
    sku_list=[]
    with open(files_sku, 'rb') as fp:
        for row in csv.DictReader(fp):
            sku_list.append(row['CONFIGS'])
        return sku_list

def _create_compare_title(files, header=True):
    with open(files, 'rb') as fp:
        try:
            for row in csv.reader(fp):
                if header:
                    return row
                    header = False
        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (files, reader.line_num, e))
        except Exception, e:
            raise e
    fp.close()

def _create_compare_list(sku, files):
    sku_dict={}
    with open(files, 'rb') as fp:
        reader = csv.reader(fp)
        try:
            compoment_list=[]
            for row in reader:
                data = ''
                if sku in row[len(TITLE_list)-1]: #TITLE_LISTä½ç½®
                    for x in xrange(0,len(row)-1): #?ªæˆª?–ITEM,COMPONENT,APPLE PN,PPN
                        data += row[x]+', '
                    compoment_list.append(data)
            sku_dict.setdefault(sku, compoment_list)
        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (files, reader.line_num, e))
    return sku_dict

def create_compare_data(FILE='PANTHER.csv', FILEOUT='PANTHER_comp_new.csv', header=True):
    log_message("Start create compare data "+FILE+" OUT = "+FILEOUT)
    try: 
        with open(FILE, 'rb') as fp: 
            with open(FILEOUT, 'wb') as fpout:       
                for row in csv.DictReader(fp): 
                    if header:
                        for column in TITLE_list:
                            if (column == 'SKU'):
                                fpout.write(column)
                            else:
                                fpout.write(column+',')
                        fpout.write('\r\n')
                    for column in TITLE_list:
                        if (column == 'SKU'): 
                            fpout.write(row[column])
                        else:
                            fpout.write(row[column]+',')
                    fpout.write('\r\n')
                    header = False
                
    except csv.Error as e:
        print ('file {0}, line {1}: {2}'.format(FILE, csv.line_num, e))
        sys.exit(255)

    except KeyError, e:
        print("FAILED, KeyError:\n{0}".format(e))
        #return e.args
        sys.exit(255)

def main(compare_out=COMPARE_OUT):
    sku_color = 0
    
    s1 = set(_create_sku_list(files_sku='PANTHER_SKU.csv'))
    s2 = set(_create_sku_list(files_sku=BUILD+'/PANTHER_SKU.csv'))

    _title = _create_compare_title(files='PANTHER_comp_new.csv')
    title=[]
    
    for row in _title:
        title.append(HTML.TableCell(row, bgcolor='Blue', style='font-family:Calibri;font-size: 15px'))

    title.insert(0, HTML.TableCell("STATUS", bgcolor='Blue', style='font-family:Calibri;font-size: 15px'))
    title.insert(0, HTML.TableCell("CONFIGS", bgcolor='Blue', style='font-family:Calibri;font-size: 15px'))
    title.pop()
    #table_data = [ title ]
    table_data = []
    
    with codecs.open(compare_out, 'wb', 'utf-8') as fp:
        
        print "New configs(sku) = {0}".format(list(s1.difference(s2)))
        print "All configs list = {0}".format(list(s1.union(s2))) #//?¯é?,?€??

        sku_list = list(s1.intersection(s2))
        #sku_list = list(s1.symmetric_difference(s2))
    
        for x in xrange(0,len(sku_list)):
            sku = sku_list[x]
            sku_dict_new = _create_compare_list(sku=sku, files='PANTHER_comp_new.csv')
            sku_dict_old = _create_compare_list(sku=sku, files='PANTHER_comp_old.csv')

            for k_new, v_new in dict(sku_dict_new).iteritems():
                s1 = set(v_new)
            for k_old, v_old in dict(sku_dict_old).iteritems():
                s2 = set(v_old)
            
            if (cmp(v_new, v_old) == 0):
                pass
            else:
                if sku_color % 2 == 0:
                    sku_cell = HTML.TableCell(sku, bgcolor='White')
                elif sku_color % 2 == 1:
                    sku_cell = HTML.TableCell(sku, bgcolor='Aqua')   
                sku_color += 1

                print("Config_SKU:{0}".format(sku))
                print("Config_SKU_CELL:{0}".format(sku_cell))

                s3 = list(s1.symmetric_difference(s2)) #//å¤§å®¶?½æ??‰ç?
                #s3 = sorted(list(s1.symmetric_difference(s2)), reverse=False)
                #s3 = sorted(list(s1.symmetric_difference(s2)), key = lambda x : x[0])

                print s3
                #?™æ®µ?¨å»ºç«‹ä??‹dictæ±ºå??¯å“ª?‹group(new/old, add/remove)
                comp_ref={}
                item_ref=[]
                for x in xrange(0,len(s3)):
                    data_ck = s3[x].split(',')
                    comp = str(data_ck[0])+str(data_ck[1])
                    if comp not in comp_ref:
                        comp_ref.setdefault(comp, 1)
                        item_ref.append(comp)
                    elif comp in comp_ref: #and item_ref.count(comp) >= 1:  #//?™è£¡?‰å€‹æ?è¶?œ°???Ÿæœ¬?³ç”¨countç¢ºè?new old
                        count = int(comp_ref[comp]) + 1
                        comp_ref[comp] = count

                #print comp_ref
                #print item_ref
                '''
                ?¦ä?ç¨®å¯«æ³?
                for x in xrange(0,len(s3)):
                    data_ck = s3[x].split(',')
                    comp = str(data_ck[0])+str(data_ck[1])
                    if not comp_ref.has_key(comp):
                        comp_ref.setdefault(comp, 1)
                        item_ref.append(comp)
                    elif comp_ref.has_key(comp):
                        count = int(comp_ref[comp]) + 1
                        comp_ref[comp] = count
                '''
                
                for k, v in dict(comp_ref).iteritems():
                    group_new=[]
                    group_old=[]
                    group = False
                    for x in xrange(0,len(s3)):
                        data = s3[x].split(',')
                        data_comp = str(data[0])+str(data[1])               
                        if k == data_comp:
                        #if k in s3[x] and v == 2:
                            if v == 2:
                                group = True
                                if s3[x] in s2:
                                    print "Old: "+s3[x]
                                    group_old.append(data)
                                if s3[x] in s1:
                                    print "New: "+s3[x]
                                    group_new.append(data)   
                            if v != 2 :
                            #if k in s3[x] and v != 2 :
                                if s3[x] in s1:
                                    print "Add: "+s3[x]
                                    data.insert(0, HTML.TableCell("Add", bgcolor='Lime'))
                                    data.insert(0, sku_cell)
                                    data.pop()
                                    table_data.append(data)
                                    #fp.write('Add:    '+ str(s3[x]) + '\n')
                                if s3[x] in s2:
                                    print "Remove: "+s3[x]
                                    data.insert(0, HTML.TableCell("Remove", bgcolor='Red'))
                                    data.insert(0, sku_cell)
                                    data.pop()
                                    table_data.append(data)
                                    #fp.write('Remove: '+ str(s3[x]) + '\n')       
                    if group:
                        if len(group_new) == 1 and len(group_old) == 1:
                            print "New: " + str(group_new[0])
                            group_new[0].insert(0, HTML.TableCell("New", bgcolor='Silver'))
                            group_new[0].insert(0, sku_cell)
                            group_new[0].pop()
                            table_data.append(group_new[0])
                            print "Old: " + str(group_old[0])
                            group_old[0].insert(0, HTML.TableCell("Old", bgcolor='Yellow'))
                            group_old[0].insert(0, sku_cell)
                            group_old[0].pop()
                            table_data.append(group_old[0])
                        elif len(group_new) == 2 and len(group_old) == 0:
                            print "Add: " + str(group_new[0])
                            group_new[0].insert(0, HTML.TableCell("Add", bgcolor='Lime'))
                            group_new[0].insert(0, sku_cell)
                            group_new[0].pop()
                            table_data.append(group_new[0])
                            print "Add: " + str(group_new[1])
                            group_new[1].insert(0, HTML.TableCell("Add", bgcolor='Lime'))
                            group_new[1].insert(0, sku_cell)
                            group_new[1].pop()
                            table_data.append(group_new[1])
                        elif len(group_new) == 0 and len(group_old) == 2:
                            print "Remove: " + str(group_old[0])
                            group_old[0].insert(0, HTML.TableCell("Remove", bgcolor='Red'))
                            group_old[0].insert(0, sku_cell)
                            group_old[0].pop()
                            table_data.append(group_old[0])
                            print "Remove: " + str(group_old[1])
                            group_old[1].insert(0, HTML.TableCell("Remove", bgcolor='Red'))
                            group_old[1].insert(0, sku_cell)
                            group_old[1].pop()
                            table_data.append(group_old[1])
        
        htmlcode = HTML.table(table_data, 
            header_row = title,
            col_styles=['font-family:Calibri;font-size: 13px', 'font-family:Calibri;font-size: 13px',
            'font-family:Calibri;font-size: 13px', 'font-family:Calibri;font-size: 13px', 
            'font-family:Calibri;font-size: 13px', 'font-family:Calibri;font-size: 13px',
            'font-family:Calibri;font-size: 13px', 'font-family:Calibri;font-size: 13px', 
            'font-family:Calibri;font-size: 13px'])
        fp.write(htmlcode) 
        #fp.write(htmlcode + '<p>\n') 
    fp.close()   
    return htmlcode
    
def Send_mail(title, to, sender, content):
    _title = title
    _to = to
    _sender = sender
    _content = content

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
        smt_ret = SMTPServer(_title,"bg3_ptd@pegatroncorp.com",_to,_content + "By " +_sender)
        return smt_ret
    
    except Exception, e:
        print("SMTP Server FAIL: \n{0}".format(e))
        return e.args

def PD_CK_RUN(title, mail_to, sender):
    
    create_compare_data(FILE='PANTHER.csv', FILEOUT='PANTHER_comp_new.csv', header=True)
    create_compare_data(FILE=BUILD+'/PANTHER.csv', FILEOUT='PANTHER_comp_old.csv', header=True)
    read_data = main()
    ret = Send_mail(title, mail_to, sender, read_data)
    
    ''' #å¤šä?æ¬¡é?æª”è?æª”æµªè²»è??¶é?
    with open(COMPARE_OUT, 'rb') as fp:
        read_data = fp.read()
        ret = Send_mail(title, mail_to, sender, read_data)
        #ret = Send_mail(title, mail_to, sender, read_data.encode('utf-8'))
    fp.close()
    '''

if __name__ == '__main__':
    
    '''
    create_compare_data(FILE='PANTHER.csv', FILEOUT='PANTHER_comp_new.csv', header=True)
    create_compare_data(FILE=BUILD+'/PANTHER.csv', FILEOUT='PANTHER_comp_old.csv', header=True)
    main()
    '''
    print FILE_NAME
    print FILE_NAME_OLD

    FILE_NAME = str(FILE_NAME).split("(")
    FILE_NAME = FILE_NAME[2]
    FILE_NAME = str(FILE_NAME).replace(").xlsx","")

    FILE_NAME_OLD = str(FILE_NAME_OLD).split("(")
    FILE_NAME_OLD = FILE_NAME_OLD[2]
    FILE_NAME_OLD = str(FILE_NAME_OLD).replace(").xlsx","")

    if os.path.isfile(SOURCE): 
        newpath = BUILD + r'/' + FILE_NAME
        if not os.path.exists(newpath): os.makedirs(newpath)
        print 'Copy files {0},{1},{2} to {3}\n'.format(SOURCE, SKU_SOURCE, CONFIGS_LIST, newpath)
        shutil.copy(SOURCE,newpath)
        shutil.copy(SKU_SOURCE,newpath)
        shutil.copy(CONFIGS_LIST,newpath)
    else:
        print 'Not exist files {0}'.format(SOURCE)
        sys.exit(255)
    
    with open('mail.txt', 'rb' ) as fp:
        mail_list = fp.read()
    fp.close()
    
    mail_list = mail_list.split(',')

    PD_CK_RUN('[Panther]P2-è«‹ç??³ä¿®?¹å·¥??BM '+FILE_NAME_OLD + ' to BM ' + FILE_NAME+')',
    mail_list, 'PD BM Notice System v1.00e')