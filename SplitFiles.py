import os

YYYYMMDD = raw_input('Please input the date as YYYYMMDD format:')
path = 'C:/AMSplit/%s/' % YYYYMMDD
files = os.listdir(path)
f1 = open('C:/AMSplit/result/Topup_from_SDP_%s.txt' % YYYYMMDD,'w')
f2 = open('C:/AMSplit/result/addnext_%s.txt' % YYYYMMDD, 'w')
f2.write('These data belongs to %d:\n' % (int(YYYYMMDD)+1))
am = 0

for f in files:
    fo = open(path+f, 'r')
    for line in fo.readlines()[1:]:
        l = line.split('|')
        if l[0][:8] == YYYYMMDD:
            f1.write('%s|%s|%s|%s|%s|%s\n' % (l[0], l[5], l[11], l[12], l[16], l[17]))
            am = int(l[11])+am
        else:
            f2.write(line)
    fo.close()
    
print 'Total recharge amount on %s:' % YYYYMMDD, am
f1.close()
f2.close()
print 'Done'