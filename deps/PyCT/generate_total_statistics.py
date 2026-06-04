import os

class JumpOutOfLoop(Exception): pass

data = [['Project', 'Line Coverage', '# of SAT', 'Running Time']]
for item in os.listdir('./project_statistics'):
    if os.path.isdir(os.path.join('./project_statistics', item)):
        try:
            first_layer = True; data2 = [item]; num = 0
            for dirpath, _, _ in os.walk('./project_statistics/' + item):
                if first_layer:
                    first_layer = False
                    try:
                        with open(dirpath + '/inputs_and_coverage.txt', 'r') as f:
                            lines = f.read().splitlines()
                            data2.append(lines[-2].replace('Total line coverage ', ''))
                            data2.append(lines[-1].replace('Time(sec.): ', ''))
                    except:
                        raise JumpOutOfLoop()
                    continue
                try:
                    with open(dirpath + '/smt.csv', 'r') as f:
                        lines = f.read().splitlines()
                        num += int(lines[1].split(',')[1])
                except: pass
            data2.insert(-1, num)
            data.append(data2)
        except JumpOutOfLoop: pass

import csv
with open('./project_statistics/total_statistics.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows([data[0]] + sorted(data[1:]))
