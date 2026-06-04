#!/usr/bin/env python3
from to_be_imported import *

SINGLE_TIMEOUT = 15; testing_mode = False # default mode, this is better since a function may cover places of another function where that function cannot cover by itself.
toolname = 'pyexz3' if args.mode == '2' else 'pyct'
exe = f'./{toolname}.py'

def f1(r0, r):
    if r0.poll(SINGLE_TIMEOUT + 5): # may get stuck here for some unknown reason
        return r.recv()

# Logging output section
if os.path.isfile(f'paper_statistics/{toolname}_run_{project_name}.csv') and os.path.isdir(f'paper_statistics/{toolname}_run_{project_name}'):
    os.system(f'rm -r paper_statistics/{toolname}_run_{project_name}*')
if not os.path.isdir(f'paper_statistics/{toolname}_run_{project_name}'):
    os.system(f'mkdir -p paper_statistics/{toolname}_run_{project_name}')

total_lines = 0
missing_lines = 0
func_inputs = {}
all_function_ranges_wrt_file = {}
coverage_data = coverage.CoverageData()
coverage_accumulated_missing_lines = {}
cov = coverage.Coverage(data_file=None, source=[rootdir], omit=['**/__pycache__/**', '**/.venv/**'])
with open(f'./project_statistics/{project_name}/incomplete_functions.txt', 'w') as fmf:
    start2 = time.time(); _id = '0'
    for dirpath, _, files in os.walk(f"./project_statistics/{project_name}"):
        for file in files:
            status = 0; our_filename = rootdir + '/' + dirpath.split('/')[-2].replace('.', '/') + '.py'
            if testing_mode and (file == 'missing_lines.txt'): status = 1
            if not testing_mode and (file == 'inputs.pkl'): status = 2
            if status > 0:
                with open(os.path.abspath(dirpath + '/inputs.pkl'), 'rb') as f:
                    func_inputs[(dirpath.split('/')[-2], dirpath.split('/')[-1])] = pickle.load(f)
                with open(os.path.abspath(dirpath + '/smt.csv'), 'r') as f:
                    lines = list(map(lambda x: x.strip(), f.readlines()))
                    b = int(lines[1].split(',')[1]); c = float(lines[1].split(',')[2]); cdivb = c / b if b else 0
                    d = int(lines[2].split(',')[1]); e = float(lines[2].split(',')[2]); edivd = e / d if d else 0
                    F = int(lines[3].split(',')[1]); g = float(lines[3].split(',')[2]); gdivF = g / F if F else 0
            if status == 1: # Mode 1
                with open(os.path.abspath(dirpath + '/' + file), 'r') as f:
                    mylist, b = map(lambda x: eval(x.strip()), f.readlines())
                    missing_lines += len(mylist)
                    total_lines += len(b)
            ############################################################################################################################
            if status == 2: # Mode 2
                start = time.time()
                for i in func_inputs[(dirpath.split('/')[-2], dirpath.split('/')[-1])]:
                    r, s = multiprocessing.Pipe(); r0, s0 = multiprocessing.Pipe(); r2, s2 = multiprocessing.Pipe()
                    def child_process():
                        sys.dont_write_bytecode = True # same reason mentioned in the concolic environment
                        cov.start()
                        module = get_module_from_rootdir_and_modpath(rootdir, dirpath.split('/')[-2])
                        execute = get_function_from_module_and_funcname(module, dirpath.split('/')[-1], False)
                        this_function_source_lines = inspect.getsourcelines(execute)
                        s2.send(set(cov.analysis(module.__file__)[1]) & set(range(this_function_source_lines[1], this_function_source_lines[1] + len(this_function_source_lines[0])))) # the result should remain the same for all inputs
                        pri_args, pri_kwargs = complete_primitive_arguments(execute, i)
                        try:
                            print('>>>', module, execute, pri_args, pri_kwargs)
                            func_timeout.func_timeout(SINGLE_TIMEOUT, execute, args=pri_args, kwargs=pri_kwargs)
                        except: pass
                        cov.stop(); coverage_data.update(cov.get_data())
                        for file in coverage_data.measured_files(): # "file" is absolute here.
                            _, _, missing_lines, _ = cov.analysis(file)
                            if file not in coverage_accumulated_missing_lines:
                                coverage_accumulated_missing_lines[file] = set(missing_lines)
                            else:
                                coverage_accumulated_missing_lines[file] &= set(missing_lines)
                        s0.send(0) # just a notification to the parent process that we're going to send data
                        s.send((coverage_data, coverage_accumulated_missing_lines))
                    process = multiprocessing.Process(target=child_process); process.start()
                    this_function_range = r2.recv()
                    if our_filename not in all_function_ranges_wrt_file:
                        all_function_ranges_wrt_file[our_filename] = this_function_range
                    else:
                        all_function_ranges_wrt_file[our_filename] |= this_function_range
                    try: (coverage_data, coverage_accumulated_missing_lines) = func_timeout.func_timeout(SINGLE_TIMEOUT + 5 + 1, f1, args=(r0, r))
                    except: pass
                    r.close(); s.close(); r0.close(); s0.close()
                    if process.is_alive(): process.kill()
                    finish = time.time()
                    if finish - start > TOTAL_TIMEOUT: break
                    if len(coverage_accumulated_missing_lines[our_filename] & this_function_range) == 0: break
                # if time.time() - start2 > 3 * 60 * 60: break
                mylist = sorted(coverage_accumulated_missing_lines[our_filename] & this_function_range)
                # mkdir -p paper_statistics && echo "ID|Function|Line Coverage|Time (sec.)|# of SMT files|# of SAT|Time of SAT|# of UNSAT|Time of UNSAT|# of OTHERWISE|Time of OTHERWISE" > output.csv2 && dump=True python3 measure_coverage.py 1 ../04_Python && cp /dev/null paper_statistics/pyct_run_04Python.csv && cat *.csv >> output.csv2 && rm -f *.csv && mv output.csv2 paper_statistics/pyct_run_04Python.csv
                _id = str(int(_id) + 1).zfill(3)
                col_1 = "{}/{} ({:.2%})".format(len(this_function_range - coverage_accumulated_missing_lines[our_filename]), len(this_function_range), (len(this_function_range - coverage_accumulated_missing_lines[our_filename])/len(this_function_range)) if len(this_function_range) > 0 else 0)
                if True: #os.environ.get('dump', False):
                    with open(f'paper_statistics/{toolname}_run_{project_name}/{_id}.csv', 'w') as f:
                        f.write(f"{_id}|{dirpath.split('/')[-2] + '.' + dirpath.split('/')[-1]}|{col_1}|{round(finish-start, 2)}|{b+d+F}|{b}|{round(cdivb, 2)}|{d}|{round(edivd, 2)}|{F}|{round(gdivF, 2)}\n")
            if status > 0:
                try: n = min(mylist)
                except: n = 0
                # if n == 0: print(len(func_inputs[(dirpath.split('/')[-2], dirpath.split('/')[-1])]))
                if args.mode == '2':
                    print(f"{our_filename}:{n}, {dirpath.split('/')[-1]}, {mylist}, {exe} -r {rootdir} '{dirpath.split('/')[-2]}' -s {dirpath.split('/')[-1]} {{}} --lib '{lib}' --total_timeout={TOTAL_TIMEOUT}", file=fmf)
                else:
                    print(f"{our_filename}:{n}, {dirpath.split('/')[-1]}, {mylist}, {exe} -r {rootdir} '{dirpath.split('/')[-2]}' -s {dirpath.split('/')[-1]} {{}} --lib '{lib}' --include_exception --total_timeout={TOTAL_TIMEOUT}", file=fmf)
end = time.time()
print(f"Time(sec.): {end-start2}") # total time to test all inputs

content = ''
for dirpath, _, files in os.walk(f"./project_statistics/{project_name}"):
    for file in files:
        if file == 'exception.txt':
            with open(os.path.join(dirpath, file), 'r') as f:
                for e in f.readlines():
                    content += e
with open(os.path.abspath(f"./project_statistics/{project_name}/exceptions.txt"), 'w') as f:
    f.write(content)

if testing_mode:
    executed_lines = total_lines - missing_lines
else:
    total_lines = 0
    missing_lines = 0
    with open(os.path.abspath(f"./project_statistics/{project_name}/missing_and_executable_lines.txt"), 'w') as f:
        for file in coverage_data.measured_files():
            if file not in all_function_ranges_wrt_file:
                executable_lines = set()
            else:
                executable_lines = set(cov.analysis(file)[1]) & all_function_ranges_wrt_file[file]
            # executable_lines = set(cov.analysis(file)[1]) # version not restricted by function ranges
            m_lines = coverage_accumulated_missing_lines[file] & executable_lines
            total_lines += len(executable_lines)
            missing_lines += len(m_lines)
            print(file, sorted(m_lines), sorted(executable_lines), file=f)
    executed_lines = total_lines - missing_lines
print("\nTotal line coverage {}/{} ({:.2%})".format(executed_lines, total_lines, (executed_lines/total_lines) if total_lines > 0 else 0))

with open(os.path.abspath(f"./project_statistics/{project_name}/inputs_and_coverage.txt"), 'w') as f:
    for (func, inputs) in func_inputs.items():
        print((rootdir + '/' + func[0].replace('.', '/') + '.py', func[1]), inputs, file=f)
    print("\nTotal line coverage {}/{} ({:.2%})".format(executed_lines, total_lines, (executed_lines/total_lines) if total_lines > 0 else 0), file=f)
    try:
        with open(os.path.abspath(f"./project_statistics/{project_name}/experiment_time.txt"), 'r') as f2:
            print(f2.readlines()[0], end='', file=f)
    except: pass

# Logging output section
os.system(f'echo "ID|Function|Line Coverage|Time (sec.)|# of SMT files|# of SAT|Time of SAT|# of UNSAT|Time of UNSAT|# of OTHERWISE|Time of OTHERWISE" > paper_statistics/{toolname}_run_{project_name}.csv')
os.system(f'cat paper_statistics/{toolname}_run_{project_name}/*.csv >> paper_statistics/{toolname}_run_{project_name}.csv')
os.system(f'rm -r paper_statistics/{toolname}_run_{project_name}')