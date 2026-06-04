#!/usr/bin/env python3
from to_be_imported import *

os.system(f"rm -rf './project_statistics/{project_name}'")

for dirpath, _, _ in os.walk(rootdir):
    dirpath = os.path.abspath(dirpath)
    if dirpath != rootdir and not dirpath.startswith(rootdir + '/.') and '__pycache__' not in dirpath: # and '.venv' not in dirpath:
        # print(dirpath)
        os.system(f"touch '{dirpath}/__init__.py'")

# Please note this function must be executed in a child process, or
# the import action will affect the coverage measurement later.
def extract_function_list_from_modpath(rootdir, modpath):
    ans = []; print(modpath, '(' + modpath.replace('.', '/') + '.py)', '==> ', end='')
    if modpath.endswith('.__init__'): return ans # an empty list here
    try:
        mod = func_timeout.func_timeout(10, get_module_from_rootdir_and_modpath, args=(rootdir, modpath,))
        print(mod, end='')
        for _, obj in inspect.getmembers(mod):
            if inspect.isclass(obj):
                for _, o in inspect.getmembers(obj):
                    if (inspect.isfunction(o) or inspect.ismethod(o)) and o.__module__ == modpath: # and inspect.signature(o).parameters:
                        ans.append(o.__qualname__)#; print(o.__qualname__)
            elif (inspect.isfunction(obj) or inspect.ismethod(obj)) and obj.__module__ == modpath: # and inspect.signature(obj).parameters:
                ans.append(obj.__qualname__)#; print(obj.__qualname__)
        i = 0
        while i < len(ans):
            if '<locals>' in ans[i]: del ans[i]; continue # cannot access nested functions
            if get_function_from_module_and_funcname(mod, ans[i], False) is None: del ans[i]; continue # similar to assert
            if len(ans[i].split('.')) == 2:
                (a, b) = ans[i].split('.')
                if b.startswith('__') and not b.endswith('__'): b = '_' + a + b
                ans[i] = a + '.' + b
            i += 1
    except func_timeout.FunctionTimedOut: pass
    except Exception as e:
        print('Exception: ' + str(e), end='', flush=True)
        print('\nWe\'re going to get stuck here...', flush=True)
        import traceback; traceback.print_exc()
        while True: pass
        # if 'No module named' in str(e):
        #     print(' Raise Exception!!!', end='')
        #     raise e
    print()
    return ans

cont = False
start = time.time()
try:
    for dirpath, _, files in os.walk(rootdir):
        dirpath += '/'
        for file in files:
            if file.endswith('.py'):
                modpath = os.path.abspath(dirpath + file)[len(rootdir) + 1:-3].replace('/', '.')
                if not modpath.startswith('.venv') and '__pycache__' not in modpath:
                    # if 'solutions.system_design.mint.mint_mapreduce' not in modpath: continue #cont = True
                    # if not cont: continue
                    if args.mode == '1': cmd = f"./pyct.py -r '{rootdir}' '{modpath}' --total_timeout {TOTAL_TIMEOUT} {{}} --lib '{lib}' --include_exception --dump_projstats"
                    elif args.mode == '2': cmd = f"./pyexz3.py -r '{rootdir}' '{modpath}' --total_timeout {TOTAL_TIMEOUT} {{}} --lib '{lib}' --dump_projstats"
                    else: cmd = f"./pyct.py -r '{rootdir}' '{modpath}' --total_timeout {TOTAL_TIMEOUT} {{}} -m 1 --lib '{lib}' --include_exception --dump_projstats"
                    if os.fork() == 0: # child process
                        funcs = extract_function_list_from_modpath(rootdir, modpath)
                        for f in funcs:
                            cmd2 = cmd + f" -s {f}"
                            print(modpath, '+', f, '>>>'); print(cmd2)
                            try: completed_process = subprocess.run(cmd2, shell=True, timeout=TOTAL_TIMEOUT+5, stdout=sys.stdout, stderr=sys.stderr)
                            except subprocess.CalledProcessError as e: print(e.output)
                            except: pass
                        os._exit(os.EX_OK)
                    os.wait()
                end = time.time()
                #if end - start > 3 * 60 * 60:
                #    raise JumpOutOfLoop()
except Exception as e:
    print('Exception: ' + str(e), end='', flush=True)
    import traceback; traceback.print_exc()

with open(os.path.abspath(f"./project_statistics/{project_name}/experiment_time.txt"), 'w') as f:
    print(f"Time(sec.): {end-start}", file=f)

print('End of running project.')

#os.system('python3 measure_coverage.py 1 ../04_Python')
# os.system('mkdir -p paper_statistics && echo "ID|Function|Line Coverage|Time (sec.)|# of SMT files|# of SAT|Time of SAT|# of UNSAT|Time of UNSAT|# of OTHERWISE|Time of OTHERWISE" > output.csv2 && dump=True python3 measure_coverage.py 1 ../04_Python && cp /dev/null paper_statistics/pyct_run_04Python.csv && cat *.csv >> output.csv2 && rm -f *.csv && mv output.csv2 paper_statistics/pyct_run_04Python.csv')
