#!/usr/bin/env python3

import argparse, logging, os, sys
import libct.explore

# Our main program starts now!
f = argparse.RawTextHelpFormatter._split_lines
argparse.RawTextHelpFormatter._split_lines = lambda *args, **kwargs: f(*args, **kwargs) + ['']
parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

# positional arguments
parser.add_argument("modpath", metavar="path.to.module", help="import path to the target module (file) relative to the project root\nEx1: ./a/b/c.py -> a.b.c\nEx2: ./def.py -> def")
parser.add_argument("input", metavar="input_dict", help="dictionary of initial arguments to be passed into the target function\nPlease note that the double quotes enclosing the dictionary cannot be omitted!\nEx1: func(a=1,b=2) -> \"{'a':1,'b':2}\"\nEx2: func(a='',b='') -> \"{'a':'','b':''}\"\n\nIf a function parameter is not assigned in this dictionary, the program will first\ncheck if it has a type annotation. If it does, the program will use the corresponding\nconstructor as its default value. For example, int() returns 0 and str() returns an\nempty string. Otherwise the program continues to check if it provides a default value.\nIf it does, the default value will be used directly. Otherwise the program simply uses\nan empty string as its default value.")

# optional arguments
parser.add_argument("--dump_projstats", dest="dump_projstats", action='store_true', help="dump project statistics under the directory \"./project_statistics/{ProjectName}/{path.\nto.module}/{FUNC}/\"")
parser.add_argument("--file_as_total", dest="file_as_total", action='store_true', help="By default the program stops testing when the full coverage of this target function is\nachieved. If this option is enabled, the program stops testing when the full coverage\nof this target \"file\" is achieved instead.", default=False)
parser.add_argument("-d", "--formula", dest='formula', help="name of directory or file to store smtlib2 formulas\n(*) When this argument is a pure positive integer N, it means that we only want to\nstore the N_th constraint where N is the number \"SMT-id\" shown in the log. The file\nshould be named {N}.smt2 in the current directory.\n(*) Otherwise, this argument names the directory, and all constraints will be stored\nin this directory whose names follow the rule mentioned above.\nIn either case, these *.smt2 files should be able to be called by a solver directly.", default=None)
parser.add_argument("-s", "--func", dest="func", help="name of the target function\n(*) If the function {f} is standalone, this name is {f}.\n(*) If the function {f} belongs to a class {C}, this name should be {C.f}.\n(*) If the function name is the same as that of the target file, this option can be\nsimply omitted.", default=None)
parser.add_argument("--include_exception", dest="include_exception", action='store_true', help="also update coverage statistics when the iteration is terminated by a exception.")
parser.add_argument("-m", "--iter", dest="iter", help="maximum number of iterations [default = oo]", type=int, default=0)
parser.add_argument("--lib", dest="lib", help="another library path to be inserted at the beginning of sys.path\nFor example, if the target function resides in another folder requiring a virtual\nenvironment, you may want to do \"--lib {path-to-target-root}/.venv/lib/python3.8/site-\npackages\".", default=None)
parser.add_argument("-l", "--logfile", dest='logfile', help="path to the desired log file\n(*) When this argument is an empty string, all logging messages will not be dumped\neither to screens or to files.\n(*) When this option is not set, the logging messages will be dumped to screens.", default=None)
parser.add_argument("-r", "--root", dest="root", help="path to the project root which the target function resides in [default = path/to/this/\nproject]\nThe option should always be provided if the target function resides in another folder.", default=os.path.dirname(__file__))
parser.add_argument("--safety", dest="safety", help="indicates the behavior when the values in Python and in SMTLIB2 of a concolic object\nare not equal. [default = 0]\n(0) The symbolic expression is still preserved even if the values are different.\n(1) The symbolic expression is erased if the values are different, but the program\nstill continues.\n(2) The symbolic expression is erased if the values are different, and the program\nterminates soon.\nOnly in level 0 don't we verify the return value of the target function since some\nobjects in fact are not picklable, and therefore the return value is not printed in\nthe end.", type=int, default=0)
parser.add_argument("--single_timeout", dest="single_timeout", help="timeout (sec.) for the tester to go through one iteration [default = 15]", type=int, default=15)
parser.add_argument("-t", "--timeout", dest="timeout", help="timeout (sec.) for the solver to solve a constraint [default = 10]", type=int, default=10)
parser.add_argument("--total_timeout", dest="total_timeout", help="timeout (sec.) for the tester to go through all iterations [default = 900]", type=int, default=900)
parser.add_argument("-v", "--verbose", dest='verbose', help="logging level [default = 1]\n(0) Show messages whose levels not lower than WARNING.\n(1) Show messages from (0), plus basic iteration information.\n(2) Show messages from (1), plus solver information.\n(3) Show messages from (2), plus all concolic objects' information.", type=int, default=1)

# Solver configuration
# solver=[z3seq, z3str, trauc, cvc4]
# parser.add_argument("--solver", dest='solver', help="solver type [default = cvc4]\nWe currently only support CVC4.", default="cvc4")

# Parse arguments
args = parser.parse_args()

##############################################################################
# This section creates an explorer instance and starts our analysis procedure!
funcname = t if (t:=args.func) else args.modpath.split('.')[-1]
statsdir = os.path.abspath(os.path.dirname(__file__)) + '/project_statistics/' + os.path.abspath(args.root).split('/')[-1] + '/' + args.modpath + '/' + funcname if args.dump_projstats else None
engine = libct.explore.ExplorationEngine(solver='cvc4', timeout=args.timeout, safety=args.safety,
                                           store=args.formula, verbose=args.verbose, logfile=args.logfile,
                                           statsdir=statsdir)
print("\nTotal iterations:", engine.explore(args.modpath, eval(args.input), root=args.root, funcname=args.func,
                                            max_iterations=args.iter, single_timeout=args.single_timeout, total_timeout=args.total_timeout, deadcode=set(),
                                            include_exception=args.include_exception, lib=args.lib, file_as_total=args.file_as_total)[0])
##############################################################################

################################################################
# This section prints the generated inputs and coverage results.
# print("\nGenerated inputs")
# print(engine.inputs)
# if len(engine.errors) > 0: print("\nError inputs"); print(engine.errors)
# engine.print_coverage() # Line coverage + Missing lines
# if result_list := list(zip(engine.inputs, engine.results)):
#     print("# of input vectors:", len(result_list)); print(result_list); print()
################################################################
