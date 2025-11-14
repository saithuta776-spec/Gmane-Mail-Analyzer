import sqlite3
import string 

conn = sqlite3.connect('index.sqlite')
cur = conn.cursor()

cur.execute(''' SELECT id,subject FROM Subjects ''')
subjects = {}
for message_row in cur :
    subjects[message_row[0]] = message_row[1]

# print(subjects)

cur.execute(''' SELECT subject_id FROM Messages ''')
subjectcount = {}
for message_row in cur :
    id = message_row[0]
    subject = subjects[id]
    subject= subject.translate(str.maketrans('','',string.punctuation))
    subject = subject.translate(str.maketrans('','','1234567890'))
    subject = subject.strip().lower()
    subject = subject.split()
    for word in subject :
        if len(word) < 4 : 
            continue
        subjectcount[word] = subjectcount.get(word,0) + 1

        # print(subjectcount)

ranking = sorted(subjectcount.items(), key=lambda item:item[1],reverse=True)
# print(ranking)
maxrank = None
minrank = None
maxword = None
minword = None
for subject,count in ranking[:100] :
    if maxrank is None or maxrank < count :
        maxrank = count
        maxword = subject

    if minrank is None or minrank > count :
        minrank = count 
        minword = subject

print(f'Highest : {maxword} {maxrank}')
print(f'Lowest : {minword} {minrank}')

bigsize = 100
smallsize = 20
first = True
fhand = open('gword.js','w')
fhand.write('gword = [\n')

for subject, count in ranking[:100]:
    if not first :
        fhand.write(',\n')
    first = False
    currentcount = count 

    if maxrank - minrank == 0 :
        size = bigsize

    else :
        size = ((currentcount-minrank) / (maxrank-minrank))
        size = int(size*(bigsize-smallsize)+smallsize)
        fhand.write(" {text : '"+subject+"', size: "+str(size)+"} ")

fhand.write('\n];\n')
fhand.close()
cur.close()