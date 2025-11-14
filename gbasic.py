import sqlite3

howmany = int(input('How many dump : '))

conn = sqlite3.connect('index.sqlite')
cur = conn.cursor()

cur.execute(''' SELECT id, sender FROM Senders ''')
senders = {}
for message_row in cur :
    senders[message_row[0]] = message_row[1]
# print(senders)

cur.execute(''' SELECT sender_id FROM Messages ''')
sendercount = {}
domaincount = {}
for message_row in cur :
    id = message_row[0]
    senderlist = senders[id]
    sendercount[senderlist] = sendercount.get(senderlist,0) + 1
    # print(sendercount)
    pieces = senders[id].split('@')
    if len(pieces) != 2 : continue
    # print(pieces)
    domain = pieces[1]
    domaincount[domain] = domaincount.get(domain,0)+1
# print(domaincount)

print(f'Top {howmany} email list organizations              ')
print()
ranking = sorted(sendercount.items(), key=lambda item:item[1],reverse=True)
# print(ranking)
for word,count in ranking[:howmany]:
    print(word,count)
    if sendercount[word] < 10 :
        break

print()
print(f'Top{howmany} domain list organizations \n         ')
ranking = sorted(domaincount.items(),key= lambda item:item[1],reverse=True)
# print(ranking)  

for domain,count in ranking[:howmany]:
    print(domain,count)
    if domaincount[domain] < 10 :
        break   


