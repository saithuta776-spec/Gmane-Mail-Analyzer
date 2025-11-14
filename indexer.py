import sqlite3
import re
from datetime import datetime
import dateutil.parser as parser 
import zlib

conn = sqlite3.connect('index.sqlite')
cur = conn.cursor()

cur.executescript(''' 
                  DROP TABLE IF EXISTS Messages ;
                  DROP TABLE IF EXISTS Senders ;
                  DROP TABLE IF EXISTS Subjects ;
                  DROP TABLE IF EXISTS Replies ;

                  CREATE TABLE IF NOT EXISTS Messages 
                  (id INTEGER PRIMARY KEY, guid TEXT UNIQUE,
                  date TEXT, sender_id INTEGER, subject_id INTEGER,
                  header BLOB, body BLOB
                  ) ;

                  CREATE TABLE IF NOT EXISTS Senders 
                  (id INTEGER PRIMARY KEY, sender TEXT UNIQUE) ;

                  CREATE TABLE IF NOT EXISTS Subjects 
                  (id INTEGER PRIMARY KEY, subject TEXT UNIQUE) ;

                  CREATE TABLE IF NOT EXISTS Replies 
                  (from_id INTEGER, to_id INTEGER) ;

                  ''')




                    # Phase 1 

dnsmapping = {}
conn_1 = sqlite3.connect('mapping.sqlite')
cur_1 = conn_1.cursor()

cur_1.execute(''' SELECT old,new FROM DNSMapping ''')
for row in cur_1 :
    dnsmapping[row[0].strip().lower()] = row[1].strip().lower()

# print(dnsmapping)

def fixsender(sender, allsenders = None) :
    global dnsmapping
    global mapping
    if sender is None :
        return sender
    sender = sender.strip().lower()
    sender = sender.replace("<","").replace(">","")

    if allsenders is not None and sender.endswith('gmane.org') :
        pieces = sender.split('-')
        for s in allsenders :
            if s.startswith(pieces[0]) :
                realsender = sender 
                sender = s
                break

        if realsender is None :
            for s in mapping :
                if s.startswith(pieces[0]) :
                    realsender = sender
                    sender = mapping[s]
                    break 

        if realsender is None : sender = pieces[0]

    sender_pieces = sender.split('@')
    if len(sender_pieces) != 2 :
        return sender
    domain = sender_pieces[1]
    x = domain
    domain_pieces = domain.split('.')
    if domain.endswith('.edu') or domain.endswith('.org') or domain.endswith('.com') or domain.endswith('.net') :
        domain =".".join(domain_pieces[-2:])

    else :
        domain = ".".join(domain_pieces[-3:])

    # if x != domain :
    #     print(f'Domain before cleaning : {x} vs Domain after cleaning : {domain}')

    domain = dnsmapping.get(domain,domain)
    return sender_pieces[0] + '@' + domain


mapping = {}
cur_1.execute(''' SELECT old,new FROM Mapping''')
for row in cur_1 :  
    old = fixsender(row[0])
    new = fixsender(row[1])
    mapping[old] = fixsender(new)

# print(mapping)
cur_1.close()


                    # Phase 2


conn_2= sqlite3.connect('content.sqlite')
cur_2 = conn_2.cursor()

everysenders = []
cur_2.execute(''' SELECT email FROM Messages ''')
for message_row in cur_2 :
    email = fixsender(message_row[0])
    if email is None : continue
    if 'gmane.org' in message_row : continue
    if email in everysenders : continue
    email = mapping.get(email,email)
    everysenders.append(email)

print(f'Email : {everysenders}')




                    # Phase 3 
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



def parseheader(hdr, totalsenders = None) :
    if hdr is None or len(hdr) < 1 :
        return None
    
    mail_from_header = None
    x = re.findall(r'\nFrom: .* <(\S+@\S+)>\n', hdr)
    if len(x) >= 1 :
        mail_from_header = x[0]
    else:
        x = re.findall(r'\nFrom: (\S+@\S+)\n', hdr)
        if len(x) >= 1 :
            mail_from_header= x[0]
    mail_from_header = fixsender(mail_from_header,totalsenders)

    
    date = None
    y = re.findall('\nDate: .*, (.*)\n', hdr)
    if len(y) >= 1 :
        tdate = y[0]
        tdate = tdate[:26]
        try:
            date = parsemaildate(tdate)
        except Exception as e:
            # print('Date ignored ',tdate, e)
            return None
        
    subject = None
    z = re.findall('\nSubject: (.*)\n', hdr)
    if len(z) >= 1 : subject = z[0].strip().lower()

    guid = None
    z = re.findall('\nMessage-ID: (.*)\n', hdr)
    if len(z) >= 1 : guid = z[0].strip().lower()

    
    if mail_from_header is None or subject is None or guid is None or date is None :
        return None
    return(mail_from_header,subject,guid,date)
        

senders = {}
subjects = {}
guids = {}
cur_2.execute(''' SELECT header,body,date FROM Messages ORDER BY DATE ''')
for message_row in cur_2 :
    header = message_row[0]
    parsed = parseheader(header,everysenders)
    if parsed is None : continue
    (mail_from_header,subject,guid,date) = parsed
    mail_from_header = mapping.get(mail_from_header,mail_from_header)

    # print(mail_from_header,subject,guid,date)
    

    sender_id = senders.get(mail_from_header,None)
    subject_id = subjects.get(subject,None)
    guid_id = guids.get(guid,None)

    if sender_id is None :
        cur.execute(''' INSERT OR IGNORE INTO Senders (sender) VALUES (?) ''', (mail_from_header,))
        conn.commit()
        cur.execute(''' SELECT id FROM Senders WHERE sender = ? LIMIT 1''',(mail_from_header,))
        try :
            row = cur.fetchone()
            sender_id = row[0]
            senders[email] = sender_id

        except :
            print('Cannot retrieve sender id',mail_from_header)
            continue
    
    if subject_id is None :
        cur.execute(''' INSERT OR IGNORE INTO Subjects (subject) VALUES (?) ''', (subject,))
        conn.commit()
        cur.execute(''' SELECT id FROM Subjects WHERE subject = ? LIMIT 1''',(subject,))
        try :
            row = cur.fetchone()
            subject_id = row[0]
            subjects[subject] = subject_id

        except :
            print('Cannot retrieve subject id', subject)
            continue
    # print(sender_id,subject_id)
    cur.execute(''' INSERT OR IGNORE INTO Messages (guid,date,sender_id,subject_id,header,body) 
                VALUES (?,datetime(?),?,?,?,?) ''', (guid,date,sender_id,subject_id,zlib.compress(message_row[0].encode()),
                                                     zlib.compress(message_row[1].encode()) ) )
    conn.commit()
    cur.execute(''' SELECT id FROM Messages WHERE guid = ? LIMIT 1 ''',(guid,))
    try :
        row = cur.fetchone()
        message_id = row[0]
        guid_id = message_id

    except :
        print('Cannot retrieve guid id ',guid)
        continue

cur.close()
cur_2.close()


