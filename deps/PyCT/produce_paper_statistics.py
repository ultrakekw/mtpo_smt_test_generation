#!/usr/bin/env python3
import csv, os, statistics

for pre in ('../PyExZ3/paper_statistics/pyexz3', 'paper_statistics_disable_AST/pyct', 'paper_statistics/pyct'):
    # extract LeetCode from pyct.csv
    with open(pre + '_run_pyct.csv', 'r') as inpuT, open(pre + '_run_leetcode.csv2', 'w') as out, open(pre + '_run_pyct.csv2', 'w') as out2:
        first = True
        writer = csv.writer(out, delimiter='|'); writer2 = csv.writer(out2, delimiter='|')
        for row in csv.reader(inpuT, delimiter='|'):
            if first or 'leetcode' in row[1]:
                writer.writerow(row)
            if first or 'leetcode' not in row[1]:
                writer2.writerow(row)
            first = False

    # split PythonLib from pyct.csv
    os.system('cp ' + pre + '_run_pyct.csv2 ' + pre + '_run_pyct.csv3')
    with open(pre + '_run_pyct.csv3', 'r') as inpuT, open(pre + '_run_pythonlib.csv2', 'w') as out, open(pre + '_run_pyct.csv2', 'w') as out2:
        first = True
        writer = csv.writer(out, delimiter='|'); writer2 = csv.writer(out2, delimiter='|')
        for row in csv.reader(inpuT, delimiter='|'):
            if first or 'lib_int' in row[1]:
                writer.writerow(row)
            if first or 'lib_int' not in row[1]:
                writer2.writerow(row)
            first = False
    os.remove(pre + '_run_pyct.csv3')

for solver in ('../PyExZ3/paper_statistics/pyexz3_', 'paper_statistics_disable_AST/pyct_', 'paper_statistics/pyct_'):
    os.system(f'head -n 1 {solver}run_04_Python.csv > {solver}run_total.csv3')
    os.system(f'awk FNR-1 {solver}run_pyexz3.csv >> {solver}run_total.csv3')
    os.system(f'awk FNR-1 {solver}run_04_Python.csv >> {solver}run_total.csv3')
    os.system(f'awk FNR-1 {solver}*.csv2 >> {solver}run_total.csv3')
    os.rename(f'{solver}run_total.csv3', f'{solver}run_total.csv2')

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i# + 1

def read_file_to_list(file):
    readdata = csv.reader(open(file, 'r'), delimiter='|')
    num = -1; covN = 0; covD = 0; times = []; sats = 0; unsats = 0
    for row in readdata:
        num += 1
        if num:
            covN += int(row[2].split()[0].split('/')[0])
            covD += int(row[2].split()[0].split('/')[1])
            times.append(float(row[3]))
            sats += int(row[5])
            unsats += int(row[7])
    # cov = "{}/{}".format(covN, covD)
    cov = "{}/{} ({:.2%})".format(covN, covD, (covN/covD) if covD > 0 else 0)
    return [cov, round(statistics.mean(times), 2), round(statistics.median(times), 2), str(sats) + '/' + str(unsats)]

with open('paper_total_table.csv', mode='w') as f:
    csvf = csv.writer(f)# , delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csvf.writerow(['BENCHMARK', 'No. of functions', 'Line Coverage (PyExZ3)', 'Line Coverage (PyCT with AST disabled)', 'Line Coverage (PyCT)', 'Average Time (PyExZ3)', 'Average Time (PyCT with AST disabled)', 'Average Time (PyCT)', 'Median Time (PyExZ3)', 'Median Time (PyCT with AST disabled)', 'Median Time (PyCT)', 'No. of SAT/UNSAT (PyExZ3)', 'No. of SAT/UNSAT (PyCT with AST disabled)', 'No. of SAT/UNSAT (PyCT)'])
    assert (t:=file_len('../PyExZ3/paper_statistics/pyexz3_run_pyexz3.csv')) == file_len('paper_statistics_disable_AST/pyct_run_pyexz3.csv') == file_len('paper_statistics/pyct_run_pyexz3.csv')
    csvf.writerow(['UnitTest (PyExZ3)', file_len('../PyExZ3/paper_statistics/pyexz3_run_pyexz3.csv')] + [val for pair in zip(read_file_to_list('../PyExZ3/paper_statistics/pyexz3_run_pyexz3.csv'), read_file_to_list('paper_statistics_disable_AST/pyct_run_pyexz3.csv'), read_file_to_list('paper_statistics/pyct_run_pyexz3.csv')) for val in pair])
    assert (t:=file_len('../PyExZ3/paper_statistics/pyexz3_run_pyct.csv2')) == file_len('paper_statistics_disable_AST/pyct_run_pyct.csv2') == file_len('paper_statistics/pyct_run_pyct.csv2')
    csvf.writerow(['UnitTest (PyCT)', file_len('../PyExZ3/paper_statistics/pyexz3_run_pyct.csv2')] + [val for pair in zip(read_file_to_list('../PyExZ3/paper_statistics/pyexz3_run_pyct.csv2'), read_file_to_list('paper_statistics_disable_AST/pyct_run_pyct.csv2'), read_file_to_list('paper_statistics/pyct_run_pyct.csv2')) for val in pair])
    assert (t:=file_len('../PyExZ3/paper_statistics/pyexz3_run_leetcode.csv2')) == file_len('paper_statistics_disable_AST/pyct_run_leetcode.csv2') == file_len('paper_statistics_disable_AST/pyct_run_leetcode.csv2')
    csvf.writerow(['LeetCode', file_len('../PyExZ3/paper_statistics/pyexz3_run_leetcode.csv2')] + [val for pair in zip(read_file_to_list('../PyExZ3/paper_statistics/pyexz3_run_leetcode.csv2'), read_file_to_list('paper_statistics_disable_AST/pyct_run_leetcode.csv2'), read_file_to_list('paper_statistics/pyct_run_leetcode.csv2')) for val in pair])
    assert (t:=file_len('../PyExZ3/paper_statistics/pyexz3_run_pythonlib.csv2')) == file_len('paper_statistics_disable_AST/pyct_run_pythonlib.csv2') == file_len('paper_statistics/pyct_run_pythonlib.csv2')
    csvf.writerow(['PythonCoreLib', file_len('../PyExZ3/paper_statistics/pyexz3_run_pythonlib.csv2')] + [val for pair in zip(read_file_to_list('../PyExZ3/paper_statistics/pyexz3_run_pythonlib.csv2'), read_file_to_list('paper_statistics_disable_AST/pyct_run_pythonlib.csv2'), read_file_to_list('paper_statistics/pyct_run_pythonlib.csv2')) for val in pair])
    assert (t:=file_len('../PyExZ3/paper_statistics/pyexz3_run_04_Python.csv')) == file_len('paper_statistics_disable_AST/pyct_run_04_Python.csv') == file_len('paper_statistics/pyct_run_04_Python.csv')
    csvf.writerow(['The Algorithms/Python', file_len('../PyExZ3/paper_statistics/pyexz3_run_04_Python.csv')] + [val for pair in zip(read_file_to_list('../PyExZ3/paper_statistics/pyexz3_run_04_Python.csv'), read_file_to_list('paper_statistics_disable_AST/pyct_run_04_Python.csv'), read_file_to_list('paper_statistics/pyct_run_04_Python.csv')) for val in pair])
    assert (t:=file_len('../PyExZ3/paper_statistics/pyexz3_run_total.csv2')) == file_len('paper_statistics_disable_AST/pyct_run_total.csv2') == file_len('paper_statistics/pyct_run_total.csv2')
    csvf.writerow(['TOTAL', file_len('../PyExZ3/paper_statistics/pyexz3_run_total.csv2')] + [val for pair in zip(read_file_to_list('../PyExZ3/paper_statistics/pyexz3_run_total.csv2'), read_file_to_list('paper_statistics_disable_AST/pyct_run_total.csv2'), read_file_to_list('paper_statistics/pyct_run_total.csv2')) for val in pair])

os.system('csvtool transpose paper_total_table.csv -o paper_total_table.csv2')
os.system('head -n -3 paper_total_table.csv2 > paper_total_table.csv')
os.remove('paper_total_table.csv2')