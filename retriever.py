import sqlite3 
from urllib.request import urlopen
import ssl 
import re
import dateutil.parser as parser 
from datetime import datetime
import time

def parsemaildate(md) :

    try :

        tdate = parser.parse(md)
        test_at = tdate.isoformat()
        return test_at
    
    except :
        pass

    pieces = md.split()
    notz = ".".join(pieces[:4])

    dnotz = None 
    for form in ['%d %b %Y %H %M %S','%d %b %Y %H %M %S',
                 '%d %b %y %H %M %S', '%d %b %Y %H %M %S',
                 '%d %b %Y %H %M', '%d %b %Y %H %M',
                 '%d %b %y %H %M', '%d %b %Y %H %M' ] :
        try :
            dnotz = datetime.strptime(notz,form)
            break 
        except : continue

    if dnotz is None : return None
    iso = dnotz.isoformat()

    tz = "+0000"
    try :
        tz = pieces[4]
        tzint = int(tz)
        if tzint == 0 :
            tz = "+0000"

        tzh = pieces[:3]
        tzm = pieces[3:]
        tz = tzh+ ':' + tzm
    except :
        pass
    return iso + tz
    



ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn = sqlite3.connect('content.sqlite')
cur = conn.cursor()

cur.execute(''' CREATE TABLE IF NOT EXISTS Messages 
            (id INTEGER PRIMARY KEY, email TEXT, subject TEXT,
            date TEXT,header BLOB, body BLOB) ''')

baseurl = 'http://mbox.dr-chuck.net/sakai.devel/'

start = 0
cur.execute(''' SELECT max(id) FROM Messages  ''')
try :
    row = cur.fetchone()
    if row is None :
        start = 0
        
    else :
        start = row[0]

except :
    start = 0

if start is None : start = 0

many = 0
count = 0
fail = 0
while True :
    if many < 1 :
        conn.commit()
        link = input('How many link : ')
        if len(link) < 1 :
            break 
        many = int(link)

    start += 1 
    cur.execute(''' SELECT id FROM Messages WHERE id = ? ''',(start,))
    try :
        row = cur.fetchone()
        if row is not None :
            continue
        else :
            row = None

    except : 
        row = None

    many = many -1 
    url = baseurl + str(start) + '/' + str(start+1)

    text = None
    try :
        document = urlopen(url,timeout=30,context=ctx)
        text  = document.read().decode()
        if document.getcode()!= 200 :
            print(f'Error code : {document.getcode(),{url}}')
            continue

    except InterruptedError :
        print(f'Program interrupted by error....')
        break 


    except Exception as e :
        print('Unable to retrieve or parse link')
        print(f'Error : {e}')
        fail += 1 
        if fail > 5 :
            break 
        continue
    print('-'*10)
    print(f'URL YOU RETRIEVED : {url} and text length : {len(text)}')
    # print(text)
    count += 1 

    if not text.startswith('From ') :
        print(f'Cannot find the word "From" from text')
        fail += 1 
        if fail > 5 :
            break 
        continue

    pos = text.find('\n\n')
    if pos > 0 :
        hdr = text[:pos]
        body = text[pos+2:]

    else :
        print(f'Cannot find break between header and body')
        fail += 1 
        if fail > 5 :
            break 
        continue

    # print(f'            Header          ')
    # print(hdr)
    # print()
    # print(f'            Body            ')
    # print(body)

    email = None 
    x = re.findall(r'\nFrom: .* <(.*)>\n',hdr)
    if len(x) == 1 :
        email = x[0]
        email = email.strip().lower()
        email = email.replace("<","")

    else :
        x = re.findall(r'\nFrom: (.*)\n',hdr)
        if len(x) == 1 :
            email = x[0]
            email = email.strip().lower()
            email = email.replace("<","")

    print(f'Email : {email}')

    subject = None
    y = re.findall(r'\nSubject: (.*)\n',hdr)
    if len(y) == 1 :
        subject = y[0]

    print(f'Subject : {subject}')

    date = None
    z = re.findall(r'\nDate: .*, (.*)\n',hdr)
    if len(z) == 1 :
        t_date = z[0]

    try :
        date = parsemaildate(t_date)

    except :
        print(f'Cannot parse date : {date}')
        fail += 1 
        if fail > 5 :
            break
        continue

    print(f'Date : {date}')
    fail = 0 
    cur.execute(''' INSERT OR IGNORE INTO Messages (email,subject,date,header,body) VALUES 
                (?,?,?,?,?) ''',(email,subject,date,hdr,body))
    if count == 50 :
        conn.commit()

    if count % 100 == 0 :
        print('Pausing for a bit...')
        time.sleep(3)

conn.commit()
cur.close()