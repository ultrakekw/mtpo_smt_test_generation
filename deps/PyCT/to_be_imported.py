import argparse, coverage, func_timeout, functools, importlib.util, inspect, multiprocessing, os, pickle, signal, subprocess, sys, time
# os.system('/usr/bin/Xorg -noreset +extension GLX +extension RANDR +extension RENDER -config /etc/X11/xorg.conf :1 &')

def SIGINT_handler(signum, frame):
    sys.exit(0)
signal.signal(signal.SIGINT, SIGINT_handler)

f = argparse.RawTextHelpFormatter._split_lines
argparse.RawTextHelpFormatter._split_lines = lambda *args, **kwargs: f(*args, **kwargs) + ['']
parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("mode", help="This argument is expected to be 1 or 2. \"1\" has the project measured with our tester, while \"2\"\nhas the project measured with PyExZ3.")
parser.add_argument("project", help="path to the project root folder")
args = parser.parse_args()

if args.mode != '2':
    from libct.utils import get_module_from_rootdir_and_modpath
    from libct.utils import get_function_from_module_and_funcname
    import libct.explore; complete_primitive_arguments = libct.explore.ExplorationEngine._complete_primitive_arguments
else:
    import symbolic.loader; get_module_from_rootdir_and_modpath = symbolic.loader.Loader.get_module_from_rootdir_and_modpath
    import symbolic.loader; get_function_from_module_and_funcname = symbolic.loader.Loader.get_function_from_module_and_funcname
    import symbolic.invocation; complete_primitive_arguments = symbolic.invocation.FunctionInvocation._complete_primitive_arguments

rootdir = os.path.abspath(args.project); lib = rootdir + '/.venv/lib/python3.8/site-packages'
sys.path.insert(0, lib); sys.path.insert(0, rootdir); project_name = rootdir.split('/')[-1]

TOTAL_TIMEOUT = 15 * 60
