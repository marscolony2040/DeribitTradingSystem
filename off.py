import sys
import os

print('Process Killer  ..!. (* *) .!..')
for port in sys.argv[1:]:
    msg = 'lsof -i :{}'.format(port)
    r = os.popen(msg).read()
    print(r, end='\n')
    r = [[p for p in j.split(' ') if p != ''] for j in r.split('\n') if len(j.split(' ')) > 1 and 'PID' not in j]
    p = [k[1] for k in r]
    for l in p:
        msg = 'kill -9 {}'.format(l)
        r = os.popen(msg).read()
        print(r)
print('All Selected Processes Have Died')
